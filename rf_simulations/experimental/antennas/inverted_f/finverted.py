### Import Libraries
import os, tempfile
from pylab import *

from CSXCAD  import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import *

import shutil

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'
sim_enabled = True

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
f0 = 2.5e9 # center frequency
fc = 1e9 # 20 dB corner frequency


FDTD.SetGaussExcite( f0, fc )

wavelength = C0 / (f0+fc)
wavelength_u = wavelength / unit
res_u = wavelength_u / 20

#######################################################################################################################################
# MATERIALS
#######################################################################################################################################

materialList = {}


## SUBSTRATE
substrate_epsR   = 3.38
substrate_kappa  = 1e-3 * 2*pi*2.45e9 * EPS0*substrate_epsR
materialList['substrate'] = CSX.AddMaterial( 'substrate', epsilon=substrate_epsR, kappa=substrate_kappa)

substrate_width = 80
substrate_length = 80
substrate_thickness = 1.5

## ANTENNA
materialList['ifa'] = CSX.AddMetal('ifa')
ifa_h  = 8;    # height of short circuit stub
ifa_l  = 22.5; # length of radiating element
ifa_w1 = 4;    # width of short circuit stub
ifa_w2 = 2.5;  # width of radiating element
ifa_wf = 1;    # width of feed element
ifa_fp = 4;    # position of feed element relative to short circuit stub
ifa_e  = 10;   # distance to edge

## GROUND PLANE
materialList['groundplane'] = CSX.AddMetal('groundplane')


#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################
SimBox = np.array([substrate_width*2, substrate_length*2, 150])

### * Boxes
## SUBSTRATE
start_subs = np.array([-substrate_width/2,  -substrate_length/2, 0])
stop_subs  = np.array([ substrate_width/2,   substrate_length/2, substrate_thickness])
materialList['substrate'].AddBox(priority=0, start=start_subs, stop=stop_subs )


## GROUND PLANE
start_gnd =  np.array([-substrate_width/2,  -substrate_length/2, substrate_thickness])
stop_gnd = np.array([substrate_width/2,   substrate_length/2-ifa_e,  substrate_thickness])
materialList['groundplane'].AddBox(priority=10, start=start_gnd, stop=stop_gnd )

## ANTENNA
tl = np.array([0,substrate_length/2-ifa_e,substrate_thickness]) #   % translate
# Feed
start_ifa_feed = np.array([0, 0.5, 0]) + tl
stop_ifa_feed = start_ifa_feed + np.array([ifa_wf, ifa_h-0.5, 0])
materialList['ifa'].AddBox(start=start_ifa_feed, stop=stop_ifa_feed, priority=10)

# Short circuit stub
start_ifa_sc = np.array([-ifa_fp, 0, 0]) + tl
stop_ifa_sc =start_ifa_sc + np.array([- ifa_w1, ifa_h, 0])
materialList['ifa'].AddBox(start=start_ifa_sc, stop=stop_ifa_sc, priority=10)

# Radiating element
start_ifa_rad = np.array([(-ifa_fp - ifa_w1), ifa_h, 0]) + tl
stop_ifa_rad = start_ifa_rad + np.array([ifa_l, - ifa_w2, 0])

materialList['ifa'].AddBox(start=start_ifa_rad, stop=stop_ifa_rad, priority=10)

### * GRID
from CSXCAD.SmoothMeshLines import SmoothMeshLines

third_mesh = np.array([2/3, -1/3]) * 0.5#res_u

# third_mesh_z = np.array([2/3, -1/2]) * 0.5

'''
Make sure the mesh is 1/rd inside, and 2/3rds outside the PEC boundary
'''

## SIMBOX
mesh.x = np.concatenate((mesh.x, np.array([-SimBox[0]/2, SimBox[0]/2])))
mesh.y = np.concatenate((mesh.y, np.array([-SimBox[1]/2, SimBox[1]/2])))
mesh.z = np.concatenate((mesh.z, np.array([-SimBox[2]/2, SimBox[2]/2])))


## Substrate
mesh.x = np.concatenate((mesh.x, start_subs[0]-third_mesh, stop_subs[0]+third_mesh))
mesh.y = np.concatenate((mesh.y, start_subs[1]-third_mesh, stop_subs[1]+third_mesh))
mesh.z = np.concatenate((mesh.z, start_subs[2]-third_mesh, stop_subs[2]+third_mesh))

## Antenna
mesh.x = np.concatenate((mesh.x, start_ifa_feed[0]-third_mesh, stop_ifa_feed[0]+third_mesh,
						start_ifa_sc[0]-third_mesh, stop_ifa_sc[0]+third_mesh,
						start_ifa_rad[0]-third_mesh, stop_ifa_rad[0]-third_mesh))

mesh.y = np.concatenate((mesh.y, start_ifa_feed[1]-third_mesh, stop_ifa_feed[1]+third_mesh,
						start_ifa_sc[1]-third_mesh, stop_ifa_sc[1]+third_mesh,
						start_ifa_rad[1]-third_mesh, stop_ifa_rad[1]-third_mesh))

mesh.z = np.concatenate((mesh.z, start_ifa_feed[2]-third_mesh, stop_ifa_feed[2]+third_mesh,
						start_ifa_sc[2]-third_mesh, stop_ifa_sc[2]+third_mesh,
						start_ifa_rad[2]-third_mesh, stop_ifa_rad[2]-third_mesh))




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
portin_start = np.array([0, 0, 0]) + tl
portin_stop  = portin_start + np.array([ifa_wf, 0.5, 0])

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


ports['portin'] = FDTD.AddLumpedPort(port_nr=1, R=feed_R, start=portin_start, stop=portin_stop, p_dir='y', excite=1, priority=portin_prio)

#######################################################################################################################################
# DUMPS
#######################################################################################################################################
dumps = {}
# add a nf2ff calc box; size is 3 cells away from MUR boundary condition
start_nf2ff = np.array([mesh.x[4],     mesh.y[4],     mesh.z[4]])
stop_nf2ff  = np.array([mesh.x[-3], mesh.y[-3], mesh.z[-3]])
dumps['nf2ff'] = FDTD.CreateNF2FFBox('nf2ff', start_nf2ff, stop_nf2ff)

# add an electric field dump just above the antenna
start_ebox = np.array([mesh.x[4] , mesh.y[4], substrate_thickness+1])
stop_ebox  = np.array([mesh.x[-3], mesh.y[-3], substrate_thickness+1])
dumps['et'] = CSX.AddDump( 'Et_', dump_mode=2 ) # cell interpolated
dumps['et'].AddBox(start_ebox, stop_ebox, priority=0 )
dumps['ht'] = CSX.AddDump(  'Ht_', dump_type=1, dump_mode=2 ) # cell interpolated
dumps['ht'].AddBox(start_ebox, stop_ebox, priority=0 )

#######################################################################################################################################
# RUN
#######################################################################################################################################


### Run the simulation
if sim_enabled:
    CSX_file = os.path.join(Sim_Path, 'inverted_f.xml')
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