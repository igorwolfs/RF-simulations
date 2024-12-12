### Import Libraries
import os, tempfile
from pylab import *

from CSXCAD  import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import *

import shutil

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'
sim_enabled = True

HALF_WAVE = 0
FULL_WAVE = 1
DIPOLE_TYPE = HALF_WAVE


### CONSTANTS
from openEMS.physical_constants import *
unit = 1e-3 # specify everything in um

## SIMULATION FOLDER SETUP
currDir = os.getcwd()
file_name = os.path.basename(__file__).strip('.py')
Plot_Path = os.path.join(currDir, file_name)
Sim_Path = os.path.join(Plot_Path, file_name)
if sim_enabled:
	if not (os.path.exists(Plot_Path)):
		os.mkdir(Plot_Path)
		os.mkdir(Sim_Path)
	else:
		shutil.rmtree(Sim_Path)
		os.mkdir(Sim_Path)

### FDTD setup
CSX = ContinuousStructure()
## * Limit the simulation to 30k timesteps
## * Define a reduced end criteria of -40dB
max_timesteps = 60000
end_criteria = 1e-4
FDTD = openEMS(NrTS=max_timesteps, EndCriteria=end_criteria)
FDTD.SetCSX(CSX)

#######################################################################################################################################
# BOUNDARY CONDITIONS
#######################################################################################################################################
FDTD.SetBoundaryCond( ['MUR', 'MUR', 'MUR', 'MUR', 'MUR', 'MUR'] )


#######################################################################################################################################
# COORDINATE SYSTEM
#######################################################################################################################################
def mesh():
	x,y,z
      

openEMS_grid = CSX.GetGrid()
openEMS_grid.SetDeltaUnit(unit)


mesh.x = np.array([])
mesh.y = np.array([])
mesh.z = np.array([])

#######################################################################################################################################
# EXCITATION Gaussian
#######################################################################################################################################

# setup FDTD parameter & excitation function
f0 = 1.5e9 # center frequency
fc = 1e9 # 20 dB corner frequency


FDTD.SetGaussExcite( f0, fc )

wavelength = C0 / (f0+fc)
wavelength_u = wavelength / unit
res_u = wavelength_u / 20

#######################################################################################################################################
# MATERIALS
#######################################################################################################################################

materialList = {}

## ANTENNA
f_antenna = 1.575e9
lambda_antenna = C0 / (f_antenna)
lambda_antenna_u = lambda_antenna / unit
materialList['dip'] = CSX.AddMetal('dip')
if (DIPOLE_TYPE == HALF_WAVE):
    dipole_length = lambda_antenna_u / 2
elif (DIPOLE_TYPE == FULL_WAVE):
    dipole_length = lambda_antenna_u

# * Dimensions
dx_dip = 0
'''
 Choose the width 0 relative to the dipole height
 Question: What is the impedance of wire in free space?
'''
dz_dip = dipole_length / 2
dy_dip = dz_dip / 50

## feed
materialList['feed'] = CSX.AddMetal('feed')
'''
remove the feed.
We could in fact use a 50 ohm controlled transmission line
A simple copper plate however will likely introduce too much loss.

Feed: (x: feed direction, y: width of the dipole)
'''
dx_feed = 0
dy_feed = 20
dz_feed = 0

#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################
SimBox = np.array([dipole_length, dipole_length, dipole_length*2])


## DIP ANTENNA
start_dip = np.array([-dx_dip/2, -dy_dip/2, -dz_dip/2]) #   % translate
stop_dip = np.array([dx_dip/2, dy_dip/2, dz_dip/2])
materialList['dip'].AddBox(start=start_dip, stop=stop_dip, priority=10)
print(f"Antenna box: {start_dip} {stop_dip}")

# Feed
# * FOR NOW: excite in the z-direction
if (dx_feed == 0):
    print(f"No feed")
else:
    start_feed = (start_dip + stop_dip) / 2 + np.array([-dx_feed, -dy_feed/2, -dz_feed/2])
    stop_feed = start_feed + np.array([0, dy_feed/2, dz_feed/2])
    materialList['feed'].AddBox(start=start_feed, stop=stop_feed, priority=10)
    print(f"Feed box: {start_feed} {stop_feed}")


### * GRID
from CSXCAD.SmoothMeshLines import SmoothMeshLines

third_mesh = np.array([2/3, -1/3]) * 10#res_u

# third_mesh_z = np.array([2/3, -1/2]) * 0.5

'''
Make sure the mesh is 1/rd inside, and 2/3rds outside the PEC boundary
'''

## SIMBOX (Create grid at edges of simulation space
mesh.x = np.concatenate((mesh.x, np.array([-SimBox[0]/2, SimBox[0]/2])))
mesh.y = np.concatenate((mesh.y, np.array([-SimBox[1]/2, SimBox[1]/2])))
mesh.z = np.concatenate((mesh.z, np.array([-SimBox[2]/2, SimBox[2]/2])))


## Antenna grid
mesh.x = np.concatenate((mesh.x, start_dip[0]-third_mesh, stop_dip[0]+third_mesh))
mesh.y = np.concatenate((mesh.y, start_dip[1]-third_mesh, stop_dip[1]+third_mesh))
mesh.z = np.concatenate((mesh.z, start_dip[2]-third_mesh, stop_dip[2]+third_mesh))


## Feed
if (dx_feed == 0):
    start_feed = np.array([0, -dy_dip/2, -dz_dip/20])
    stop_feed = np.array([0, dy_dip/2, dz_dip/20])
else:
    pass


mesh.x = np.concatenate((mesh.x, start_feed[0]-third_mesh, stop_feed[0]+third_mesh))
mesh.y = np.concatenate((mesh.y, start_feed[1]-third_mesh, stop_feed[1]+third_mesh))
mesh.z = np.concatenate((mesh.z, start_feed[2]-third_mesh, stop_feed[2]+third_mesh))


#######################################################################################################################################
# PROBES
#######################################################################################################################################
ports = {}

'''
WARNING: 
-> in this case, if we don't choose our mesh size small enough, the voltage probe doesn't even get to a 1D integral, and errors ensue.
-> SO: probe errors can be a consequence of (like most erros in FDTD) incorrect meshing

'''
feed_R = 50
portin_prio = 5
if (dx_feed == 0):
    portin_start = start_feed
    portin_stop  = stop_feed
else:
    portin_start = np.array([0, start_dip[1], 0])
    portin_stop  = np.array([0, stop_dip[1], 0])

mesh.x = np.concatenate((mesh.x, portin_start[0]-third_mesh, portin_stop[0]+third_mesh, np.array([portin_start[0], portin_stop[0]])))
mesh.y = np.concatenate((mesh.y, portin_start[1]-third_mesh, portin_stop[1]+third_mesh, np.array([portin_start[1], portin_stop[1]])))
mesh.z = np.concatenate((mesh.z, portin_start[2]-third_mesh, portin_stop[2]+third_mesh, np.array([portin_start[2]])))

print(f"resolution_U: {res_u}")
print("mesh.x: {mesh.x}\r\n", mesh.x)
print("mesh.y: {mesh.y}\r\n", mesh.y)
print("mesh.z: {mesh.z}\r\n", mesh.z)

mesh.x = SmoothMeshLines(mesh.x, res_u, 1.4)
mesh.y = SmoothMeshLines(mesh.y, res_u, 1.4)
mesh.z = SmoothMeshLines(mesh.z, res_u, 1.4)

print("mesh.x: {mesh.x}\r\n", mesh.x)
print("mesh.y: {mesh.y}\r\n", mesh.y)
print("mesh.z: {mesh.z}\r\n", mesh.z)


openEMS_grid.AddLine('x', mesh.x)
openEMS_grid.AddLine('y', mesh.y)
openEMS_grid.AddLine('z', mesh.z)

print(f"Port start: {portin_start}, stop: {portin_stop}")
if (dx_feed == 0):
    ports['portin'] = FDTD.AddLumpedPort(port_nr=1, R=feed_R, start=portin_start, stop=portin_stop, p_dir='z', excite=True, priority=portin_prio)    
else:
    ports['portin'] = FDTD.AddLumpedPort(port_nr=1, R=feed_R, start=portin_start, stop=portin_stop, p_dir='x', excite=True, priority=portin_prio)

#######################################################################################################################################
# DUMPS
#######################################################################################################################################
dumps = {}
# add a nf2ff calc box; size is 3 cells away from MUR boundary condition
start_nf2ff = np.array([mesh.x[4],     mesh.y[4],     mesh.z[4]])
stop_nf2ff  = np.array([mesh.x[-3], mesh.y[-3], mesh.z[-3]])
dumps['nf2ff'] = FDTD.CreateNF2FFBox('nf2ff', start_nf2ff, stop_nf2ff)

# add an electric field dump just above the antenna
start_ebox = start_nf2ff
stop_ebox  = stop_nf2ff
dumps['et'] = CSX.AddDump( 'Et_', dump_mode=2 ) # cell interpolated
dumps['et'].AddBox(start_ebox, stop_ebox, priority=0 )
dumps['ht'] = CSX.AddDump(  'Ht_', dump_type=1, dump_mode=2 ) # cell interpolated
dumps['ht'].AddBox(start_ebox, stop_ebox, priority=0 )

#######################################################################################################################################
# RUN
#######################################################################################################################################


### Run the simulation
if sim_enabled:
    CSX_file = os.path.join(Sim_Path, file_name)
    if not os.path.exists(Sim_Path):
        os.mkdir(Sim_Path)

    CSX.Write2XML(CSX_file)
    from CSXCAD import AppCSXCAD_BIN
    os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

    # FDTD.Run(Sim_Path, cleanup=True)
    FDTD.Run(Sim_Path, cleanup=True, debug_material=True, debug_pec=True, debug_operator=True, debug_boxes=True, debug_csx=True, verbose=3)



#######################################################################################################################################
# POST_PROCESSING
#######################################################################################################################################

freq = np.linspace(max(1e9,f0-fc),f0+fc,501)
ports['portin'].CalcPort(Sim_Path, freq)

### Reflection
s11 = ports['portin'].uf_ref / ports['portin'].uf_inc
s11_dB = 20.0*np.log10(np.abs(s11))
figure()
plot(freq/1e9, s11_dB, 'k-', linewidth=2, label='$S_{11}$')
grid()
legend()
ylabel('S-Parameter (dB)')
xlabel('Frequency (GHz)')
plt.savefig(os.path.join(Plot_Path, 's_prameters.pdf'))
show()


### Impedance
Zin = ports['portin'].uf_tot / ports['portin'].if_tot
plot(freq/1e9, np.real(Zin), 'k-', linewidth=2, label='$\Re\{Z_{in}\}$')
plot(freq/1e9, np.imag(Zin), 'r--', linewidth=2, label='$\Im\{Z_{in}\}$')
grid()
legend()
ylabel('Zin (Ohm)')
xlabel('Frequency (GHz)')
plt.savefig(os.path.join(Plot_Path, 'impedance.pdf'))

show()

# Check if the reflection drops extremely low somewhere
idx = np.where((s11_dB<-10) & (s11_dB==np.min(s11_dB)))[0]
print(f"idx: {idx}")
if not len(idx)==1:
    print('No resonance frequency found for far-field calulation')
else:
    # If it does, get that frequency ((f_res = f[idx[0]]), which is the frequency where S11 is minimal.
    f_res = freq[idx[0]]
    theta = np.arange(0, 180.0, 2.0)
    phi   = [-180, 180]
    nf2ff_res = dumps['nf2ff'].CalcNF2FF(Sim_Path, f_res, theta, phi, center=[0,0,1e-3])
    figure()
	# Normalize electric field + add directivity to scale the plot so the highest value shows the actual max directivity.
    E_norm = 20.0*np.log10(nf2ff_res.E_norm[0]/np.max(nf2ff_res.E_norm[0])) + 10.0*np.log10(nf2ff_res.Dmax[0])
    plot(theta, np.squeeze(E_norm[:,0]), 'k-', linewidth=2, label='xz-plane')
    plot(theta, np.squeeze(E_norm[:,1]), 'r--', linewidth=2, label='yz-plane')
    grid()
    ylabel('Directivity (dBi)')
    xlabel('Theta (deg)')
    title('Frequency: {} GHz'.format(f_res/1e9))
    legend()
    plt.savefig(os.path.join(Plot_Path, 'e_field_resonance.pdf'))

print(f"Radiated power: {nf2ff_res.Prad}")
print(f"Directivity dmax: {nf2ff_res.Dmax}, {10*log10(nf2ff_res.Dmax)} dBi")

P_in = real(0.5 * ports['portin'].uf_tot * np.conjugate( ports['portin'].if_tot )) # antenna feed power
print(f"efficiency: nu_rad = {100*nf2ff_res.Prad/real(P_in[idx[0]])}")