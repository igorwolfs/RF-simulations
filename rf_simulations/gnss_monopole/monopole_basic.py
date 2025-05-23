"""
Goal: 
- Simulate a simple 3D monopole antenna
- The frequency of the antenna should be about 1.5 GHz (L1-GPS band)
Check the radiation pattern, and compare with the planar example.
"""

import argparse

### Import Libraries
import sys
import os, tempfile
from pathlib import Path, PurePath
from pylab import *

from CSXCAD  import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import *

import shutil

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'

sim_enabled = True


### CONSTANTS
from openEMS.physical_constants import *
unit = 1e-3 # specify everything in mm

## SIMULATION FOLDER SETUP
file_name = Path(__file__).parts[-1].strip(".py")
currDir = Path(__file__).parents[0]
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

'''
#! WARNING: 
- Using the right excitation frequency range is very important here.
'''
max_timesteps = 150000
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
# f0 = 1.5e9 # center frequency
# fc = 500e6 # 20 dB corner frequency

'''
#! WARNING: having the right 
'''
f0 = 2e9 # center frequency
fc = 1e9 # 20 dB corner frequency

FDTD.SetGaussExcite( f0, fc )


#######################################################################################################################################
# MATERIALS
#######################################################################################################################################
materialList = {}


## SUBSTRATE
substrate_epsR = 1

## ANTENNA
f_antenna = 1500e6 #! GPS L1 freq (MHz)
lambda_antenna = C0 / (f_antenna * sqrt(substrate_epsR))
lambda_antenna_u = lambda_antenna / unit

materialList['monopole'] = CSX.AddMetal( 'monopole' ) # create a perfect electric conductor (PEC)
monopole_length = (lambda_antenna_u) / 4  # quarter wavelength
dx_mon = monopole_length / 40
dy_mon = monopole_length / 40
dz_mon = monopole_length

## CREATE GROUND PLANE
materialList['gnd'] = CSX.AddMetal('gnd') # create a perfect electric conductor (PEC)
dx_gnd = monopole_length
dy_gnd = monopole_length
dz_gnd = 0

'''
WARNING: the ground plane for a microstrip patch antenna can also be too large.
'''

# size of the simulation box
SimBox = np.array([150, 150, 150])

wavelength_min = (C0/(f0+fc))
wavelength_min_u = wavelength_min / unit
resolution_u = wavelength_min_u / 20

### Generate properties, primitives and mesh-grid
# initialize the mesh with the "air-box" dimensions
mesh.x = np.concatenate((mesh.x, np.array([-SimBox[0]/2, SimBox[0]/2])))
mesh.y = np.concatenate((mesh.y, np.array([-SimBox[1]/2, SimBox[1]/2])))
mesh.z = np.concatenate((mesh.z, np.array([-SimBox[2]/2, SimBox[2]/2])))

#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################
# * ANTENNA
# upper patch
start_mon = [-dx_mon/2, -dy_mon/2, 0]
stop_mon = [dx_mon/2, dy_mon/2, dz_mon]
materialList['monopole'].AddBox(priority=10, start=start_mon, stop=stop_mon) # add a box-primitive to the metal property 'patch'
# materialList['mslfeed'].AddBox(priority=10, start=start_mslfeed, stop=stop_mslfeed) # add a box-primitive to the metal property 'patch'

# * GROUND
start_ground = [-dx_gnd/2, -dy_gnd/2, 0]
stop_ground = [dx_gnd/2, dy_gnd/2, 0]
materialList['gnd'].AddBox( priority=0, start=start_ground, stop=stop_ground)

# apply the excitation & resist as a current source
# feed_dx = -patch_dx/2 # feeding position in x-direction (assume feeding at the edge)
feed_R = 30 # feed resistance
start_port = [-dx_mon/2, -dy_mon/2, 0]
stop_port  = [dx_mon/2, dy_mon/2, dz_mon/20]
port = FDTD.AddLumpedPort(1, feed_R, start_port, stop_port, 'z', 1.0, priority=5) #, edges2grid='xy')

print(f"monopole: {start_mon} {stop_mon}")
print(f"ground: {start_ground} {stop_ground}")
print(f"port: {start_port} {stop_port}")

##! DEFINING GRID
from CSXCAD.SmoothMeshLines import SmoothMeshLines

third_array = np.array([-1/3, 2/3]) * start_mon[1]/2

# Add extra cells for supply MSL
# We probably don't need these thanks to out existing patch meshing
mesh.x = np.concatenate((mesh.x, np.array([start_mon[0], stop_mon[0]]), start_mon[0] - third_array, stop_mon[0] + third_array))
mesh.y = np.concatenate((mesh.y, np.array([start_mon[1], stop_mon[1]]), start_mon[1] - third_array, stop_mon[1] + third_array))
mesh.z = np.concatenate((mesh.z, np.array([start_mon[2], stop_mon[2]]), start_mon[2] - third_array, stop_mon[2] + third_array))

# Add extra cells from lumped port
mesh.x = np.concatenate((mesh.x, np.array([start_port[0]]), start_port[0] + third_array))
mesh.y = np.concatenate((mesh.y, np.array([start_port[1]]), start_port[1] + third_array))
mesh.z = np.concatenate((mesh.z, np.array([start_port[2], stop_port[2]]), start_port[2] - third_array, stop_port[2] + third_array))

# Add extra cells for ground
mesh.x = np.concatenate((mesh.x, np.array([start_ground[0], stop_ground[0]]) + third_array, np.array([start_ground[0], stop_ground[0]])-third_array))
mesh.y = np.concatenate((mesh.y, np.array([start_ground[1], stop_ground[1]]) + third_array, np.array([start_ground[1], stop_ground[1]])-third_array))

# Add patch 
# third_array = np.array([-resolution_u / 3, 2 * resolution_u / 3]) / 2


print(f"resolution_U: {resolution_u}")
print("mesh.x: {mesh.x}\r\n", mesh.x)
print("mesh.y: {mesh.y}\r\n", mesh.y)
print("mesh.z: {mesh.z}\r\n", mesh.z)

mesh.x = SmoothMeshLines(mesh.x, resolution_u, 1.4)
mesh.y = SmoothMeshLines(mesh.y, resolution_u, 1.4)
mesh.z = SmoothMeshLines(mesh.z, resolution_u, 1.4)

print("mesh.x: {mesh.x}\r\n", mesh.x)
print("mesh.y: {mesh.y}\r\n", mesh.y)
print("mesh.z: {mesh.z}\r\n", mesh.z)


openEMS_grid.AddLine('x', mesh.x)
openEMS_grid.AddLine('y', mesh.y)
openEMS_grid.AddLine('z', mesh.z)


#######################################################################################################################################
# DUMP BOXES
#######################################################################################################################################

nf2ff = FDTD.CreateNF2FFBox()

dump_boxes = {}
## define dump boxes
field1_start = [mesh.x[0], mesh.y[0], 0]
field1_stop  = [mesh.x[-1], mesh.y[-1], 0]

dump_boxes['et1'] = CSX.AddDump( 'Et1_', dump_mode=2 ) # cell interpolated
dump_boxes['et1'].AddBox(field1_start, field1_stop, priority=0 )

dump_boxes['ht1'] = CSX.AddDump(  'Ht1_', dump_type=1, dump_mode=2 ) # cell interpolated
dump_boxes['ht1'].AddBox(field1_start, field1_stop, priority=0 )


## define dump boxes
field2_start = [start_mon[0], mesh.y[0], mesh.z[0]]
field2_stop  = [start_mon[0], mesh.y[-1], mesh.z[-1]]

dump_boxes['et2'] = CSX.AddDump( 'Et2_', dump_mode=2 ) # cell interpolated
dump_boxes['et2'].AddBox(field2_start, field2_stop, priority=0 )

dump_boxes['ht2'] = CSX.AddDump(  'Ht2_', dump_type=1, dump_mode=2 ) # cell interpolated
dump_boxes['ht2'].AddBox(field2_start, field2_stop, priority=0 )

#######################################################################################################################################
# SIMULATION
#######################################################################################################################################

### Run the simulation
CSX_file = os.path.join(Sim_Path, 'simp_patch.xml')
if not os.path.exists(Sim_Path):
    os.mkdir(Sim_Path)
CSX.Write2XML(CSX_file)
from CSXCAD import AppCSXCAD_BIN
os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

if sim_enabled:
	FDTD.Run(Sim_Path, cleanup=True, debug_material=True, debug_pec=True, debug_operator=True, debug_boxes=True, debug_csx=True, verbose=3)

#######################################################################################################################################
# POST_PROCESSING
#######################################################################################################################################
### Run the simulation

f = np.linspace(max(1e9,f0-fc),f0+fc,401)
port.CalcPort(Sim_Path, f)
s11 = port.uf_ref/port.uf_inc
s11_dB = 20.0*np.log10(np.abs(s11))
figure()
plot(f/1e9, s11_dB, 'k-', linewidth=2, label='$S_{11}$')
grid()
legend()
ylabel('S-Parameter (dB)')
xlabel('Frequency (GHz)')
plt.savefig(os.path.join(Plot_Path, 's_prameters.pdf'))
show()

'''
Dmax: maximal directivity
=> : m_maxDir = 4*M_PI*P_max / m_radPower;
    - m_radPower: the normalized power in all directions
    - P_max: the maximum power in one specific direction in the far-field
theta: [-180 -> 180] is the angle with the z-axis
phi: [0 -> 90] is the angle in the xy plane
'''

# Check if the reflection drops extremely low somewhere
idx = np.where((s11_dB<-10) & (s11_dB==np.min(s11_dB)))[0]

print(f"Expected resonant frequency: {C0 / (sqrt(substrate_epsR)) / (dx_mon * 4)}")
if not len(idx)==1:
    print('No resonance frequency found for far-field calulation')
else:
    # If it does, get that frequency ((f_res = f[idx[0]]), which is the frequency where S11 is minimal.
    f_res = f[idx[0]]
    theta = np.arange(-180.0, 180.0, 2.0)
    phi   = [0., 90.]
    nf2ff_res = nf2ff.CalcNF2FF(Sim_Path, f_res, theta, phi, center=[0,0,1e-3])
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

Zin = port.uf_tot/port.if_tot
figure()
plot(f/1e9, np.real(Zin), 'k-', linewidth=2, label='$\Re\{Z_{in}\}$')
plot(f/1e9, np.imag(Zin), 'r--', linewidth=2, label='$\Im\{Z_{in}\}$')
grid()
legend()
ylabel('Zin (Ohm)')
xlabel('Frequency (GHz)')
plt.savefig(os.path.join(Plot_Path, 'impedance.pdf'))

show()

print(f"Radiated power: {nf2ff_res.Prad}")
print(f"Directivity dmax: {nf2ff_res.Dmax}, {10*log10(nf2ff_res.Dmax)} dBi")
