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
max_timesteps = 10000
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
f0 = 1e9 # center frequency
fc = 0.5e9 


FDTD.SetGaussExcite( f0, fc )
wavelength = C0 / (f0+fc)
wavelength_u = wavelength / unit
res_u = wavelength_u / 20

#######################################################################################################################################
# MATERIALS
#######################################################################################################################################

materialList = {}

## ANTENNA
#! 80 mm per edge
f_antenna = 868e6 #! LORAWAN freq (MHz)
lambda_antenna = C0 / (f_antenna)
lambda_antenna_u = lambda_antenna / unit
materialList['copper'] = CSX.AddMetal('PEC')#CSX.AddMaterial('copper')
# materialList['copper'].SetMaterialProperty(epsilon=1.0, mue=1.0, kappa=56e6)

dipole_length = lambda_antenna_u / 2

# * Dimensions
dx_dip = dipole_length/50
'''
 Choose the width 0 relative to the dipole height
 Question: What is the impedance of wire in free space?
'''
dy_dip = dipole_length
dz_dip = 0
dy0_dip = dx_dip

'''
remove the feed.
We could in fact use a 50 ohm controlled transmission line
A simple copper plate however will likely introduce too much loss.

Feed: (x: feed direction, y: width of the dipole)
'''
dx_feed = 5
dy_feed = dx_dip
dz_feed = 0

#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################
'''
- Why does the dipole not resonate at the required frequency?
- Which point is the excitation in fact applied?
'''

SimBox = np.array([dipole_length, 2*dipole_length, dipole_length])


## DIP ANTENNA
# Left arm
start_dip1 = np.array([-dx_dip/2, -dy_dip/2, 0])
stop_dip1 = np.array([dx_dip/2, -dy0_dip, 0])
materialList['copper'].AddBox(start=start_dip1, stop=stop_dip1, priority=10)

# Right arm
start_dip2 = np.array([-dx_dip/2, dy0_dip, 0])
stop_dip2 = np.array([dx_dip/2, dy_dip/2, 0])
materialList['copper'].AddBox(start=start_dip2, stop=stop_dip2, priority=10)


## Feed
# Left feed
start_feed1 = np.array([-dx_feed-dx_dip/2, -dy_feed-dy0_dip, 0])
stop_feed1 = np.array([-dx_dip/2, -dy0_dip, 0])
materialList['copper'].AddBox(start=start_feed1, stop=stop_feed1, priority=10)

# Right feed
#! Invert feed here
start_feed2 = np.array([-dx_feed-dx_dip/2, dy0_dip, 0])
stop_feed2 = np.array([-dx_dip/2, dy_feed+dy0_dip, 0])
materialList['copper'].AddBox(start=start_feed2, stop=stop_feed2, priority=10)

### * GRID
from CSXCAD.SmoothMeshLines import SmoothMeshLines

third_mesh = np.array([2/3, -1/3]) * dx_dip #res_u

'''
Make sure the mesh is 1/rd inside, and 2/3rds outside the PEC boundary
'''

## SIMBOX (Create grid at edges of simulation space
mesh.x = np.concatenate((mesh.x, np.array([-SimBox[0]/2, SimBox[0]/2])))
mesh.y = np.concatenate((mesh.y, np.array([-SimBox[1]/2, SimBox[1]/2])))
mesh.z = np.concatenate((mesh.z, np.array([-SimBox[2]/2, SimBox[2]/2])))

## Antenna grid
mesh.x = np.concatenate((mesh.x, start_dip1[0]-third_mesh, stop_dip1[0]+third_mesh))
mesh.y = np.concatenate((mesh.y, start_dip1[1]-third_mesh, stop_dip1[1]+third_mesh))
mesh.z = np.concatenate((mesh.z, start_dip1[2]-third_mesh, stop_dip1[2]+third_mesh))

mesh.x = np.concatenate((mesh.x, start_dip2[0]-third_mesh, stop_dip2[0]+third_mesh))
mesh.y = np.concatenate((mesh.y, start_dip2[1]-third_mesh, stop_dip2[1]+third_mesh))
mesh.z = np.concatenate((mesh.z, start_dip2[2]-third_mesh, stop_dip2[2]+third_mesh))

## Feed grid
mesh.x = np.concatenate((mesh.x, start_feed1[0]-third_mesh, stop_feed1[0]+third_mesh))
mesh.y = np.concatenate((mesh.y, start_feed1[1]-third_mesh, stop_feed1[1]+third_mesh))
mesh.z = np.concatenate((mesh.z, start_feed1[2]-third_mesh, stop_feed1[2]+third_mesh))

mesh.x = np.concatenate((mesh.x, start_feed2[0]-third_mesh, stop_feed2[0]+third_mesh))
mesh.y = np.concatenate((mesh.y, start_feed2[1]-third_mesh, stop_feed2[1]+third_mesh))
mesh.z = np.concatenate((mesh.z, start_feed2[2]-third_mesh, stop_feed2[2]+third_mesh))

## Add mesh on conductor edges
idx = 0
mesh.x = np.concatenate((mesh.x, np.array([start_dip1[idx], start_dip2[idx], start_feed1[idx], start_feed2[idx]])))
mesh.x = np.concatenate((mesh.x, np.array([stop_dip1[idx], stop_dip2[idx], stop_feed1[idx], stop_feed2[idx]])))
idx = 1
mesh.y = np.concatenate((mesh.y, np.array([start_dip1[idx], start_dip2[idx], start_feed1[idx], start_feed2[idx]])))
mesh.y = np.concatenate((mesh.y, np.array([stop_dip1[idx], stop_dip2[idx], stop_feed1[idx], stop_feed2[idx]])))
idx = 2
mesh.z = np.concatenate((mesh.z, np.array([start_dip1[idx], start_dip2[idx], start_feed1[idx], start_feed2[idx]])))
mesh.z = np.concatenate((mesh.z, np.array([stop_dip1[idx], stop_dip2[idx], stop_feed1[idx], stop_feed2[idx]])))

#######################################################################################################################################
# PROBES
#######################################################################################################################################

ports = {}

'''
WARNING: 
-> in this case, if we don't choose our mesh size small enough, the voltage probe doesn't even get to a 1D integral, and errors ensue.
-> SO: probe errors can be a consequence of (like most erros in FDTD) incorrect meshing
'''

feed_R = 200
portin_prio = 5

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


# Direction of excitation -> X
ports['portin1'] = FDTD.AddLumpedPort(port_nr=1, R=feed_R, start=start_feed1, stop=stop_feed1, p_dir='x', excite=1, priority=portin_prio)
ports['portin2'] = FDTD.AddLumpedPort(port_nr=2, R=feed_R, start=start_feed2, stop=stop_feed2, p_dir='x', excite=-1, priority=portin_prio)

#######################################################################################################################################
# Excitation
#######################################################################################################################################

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
start_ebox[0] = 0
stop_ebox  = stop_nf2ff
stop_ebox[0] = 0
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

show_freq_plots = True

################ FREQ ##################
freq = np.linspace(f0-fc,f0+fc,501)
for i in range(1,3):
    ports[f'portin{i}'].CalcPort(Sim_Path, freq)

    if (show_freq_plots):
        ### Reflection
        s11 = ports[f'portin{i}'].uf_ref / ports[f'portin{i}'].uf_inc
        s11_dB = 20.0*np.log10(np.abs(s11))
        figure()
        plot(freq/1e6, s11_dB, 'k-', linewidth=2, label='$S_{11}$')
        grid()
        legend()
        ylabel('S-Parameter (dB)')
        xlabel('Frequency (GHz)')
        plt.savefig(os.path.join(Plot_Path, f's_prameters_{i}.pdf'))
        show()
        
        ### Impedance
        Zin = ports[f'portin{i}'].uf_tot / ports[f'portin{i}'].if_tot
        plot(freq/1e6, np.real(Zin), 'k-', linewidth=2, label='$\Re\{Z_{in}\}$')
        plot(freq/1e6, np.imag(Zin), 'r--', linewidth=2, label='$\Im\{Z_{in}\}$')
        grid()
        legend()
        ylabel('Zin (Ohm)')
        xlabel('Frequency (GHz)')
        plt.savefig(os.path.join(Plot_Path, f'impedance_{i}.pdf'))

        show()

if (show_freq_plots):
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
        title('Frequency: {} GHz'.format(f_res/6))
        legend()
        plt.savefig(os.path.join(Plot_Path, 'e_field_resonance.pdf'))
        
        
        P_in = 0
        for i in range(1, 3):
            P_in += real(0.5 * ports[f'portin{i}'].uf_tot * np.conjugate( ports[f'portin{i}'].if_tot )) # antenna feed power
        print(f"efficiency: nu_rad = {100*nf2ff_res.Prad/real(P_in[idx[0]])}")

        print(f"Radiated power: {nf2ff_res.Prad}")
        print(f"Directivity dmax: {nf2ff_res.Dmax}, {10*log10(nf2ff_res.Dmax)} dBi")

################ TIME ##################
# It seems like the excitation is exactly the same, which isn't good. There is supposed to be a phaseshift and a complementary feed
### Total Current
figure()
plot(ports[f'portin{1}'].i_data.ui_time[0], ports[f'portin{1}'].it_tot, 'k-', linewidth=2, label='it_in1')
plot(ports[f'portin{2}'].i_data.ui_time[0], ports[f'portin{2}'].it_tot, 'r--', linewidth=2, label='it_in2')
grid()
legend()
ylabel('current [A]')
xlabel('Time (s)')
plt.savefig(os.path.join(Plot_Path, f't_currents.pdf'))
show()

### Total Voltage
plot(ports[f'portin{1}'].u_data.ui_time[0], ports[f'portin{1}'].ut_tot, 'k-', linewidth=2, label='ut_in1')
plot(ports[f'portin{2}'].u_data.ui_time[0], ports[f'portin{2}'].ut_tot, 'r--', linewidth=2, label='ut_in2')
grid()
legend()
ylabel('voltage [V]')
xlabel('Time (s)')
plt.savefig(os.path.join(Plot_Path, f't_voltages.pdf'))
show()
