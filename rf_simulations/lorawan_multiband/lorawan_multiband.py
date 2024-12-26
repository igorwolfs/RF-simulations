"""
Goal: 
- write the required meshing functions.
- Import the inverted F-antenna.
- Mesh the antenna.
"""

import sys
from pathlib import Path, PurePath
import os

# Add path to python
pythonpath = PurePath(Path(__file__).parents[2], 'python_libs')
sys.path.append(os.path.abspath(pythonpath))


### Import Libraries
from pylab import *

from CSXCAD  import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import *

import shutil

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'
sim_enabled = False

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

## Get models
stl_path = os.path.join(currDir, "freecad")
model_files = os.listdir(stl_path)
model_files = [file_ for file_ in model_files if file_.endswith('.stl')]

### FDTD setup
CSX = ContinuousStructure()
## * Limit the simulation to 30k timesteps
## * Define a reduced end criteria of -40dB
max_timesteps = 540000*3*3
end_criteria = 1e-4
FDTD = openEMS(NrTS=max_timesteps, EndCriteria=end_criteria)
FDTD.SetCSX(CSX)

### Antenna-settings enabled
antenna_1 = False
antenna_2 = True
antenna_3 = False

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
f0 = 0.7e9 # center frequency
fc = 0.5e9 # 20 dB corner frequency


FDTD.SetGaussExcite( f0, fc )

wavelength = C0 / (f0+fc)
wavelength_u = wavelength / unit
res_u = wavelength_u / 20

#######################################################################################################################################
# MATERIALS
#######################################################################################################################################

materialList = {}

## FR4
substrate_epsR   = 3.5
substrate_kappa  = 1e-3 * 2*pi*2.45e9 * EPS0*substrate_epsR
materialList['FR4'] = CSX.AddMaterial( 'FR4', epsilon=substrate_epsR)#, kappa=substrate_kappa)

## ANTENNA
materialList['antenna'] = CSX.AddMetal('antenna')

## FEED
materialList['gnd'] = CSX.AddMetal('gnd')

## AIR
materialList['air'] = CSX.AddMaterial('air')


#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################


polyhedrons = {}
### * Boxes
## ANTENNA PARTS
# Antenna 1
# Length = Lfeed + L1 + La1 + La2 + La3 = 

if (antenna_1):
    antenna_1_filepath = os.path.join(stl_path, "antenna_1.stl")
    polyhedrons['antenna_1']  = materialList['antenna'].AddPolyhedronReader(antenna_1_filepath,  priority=5)
    assert(polyhedrons['antenna_1'] .ReadFile(), f"Found file")

# Antenna 2
if (antenna_2):
    antenna_2_filepath = os.path.join(stl_path, "antenna_2.stl")
    polyhedrons['antenna_2']  = materialList['antenna'].AddPolyhedronReader(antenna_2_filepath,  priority=5)
    assert(polyhedrons['antenna_2'] .ReadFile(), f"Found file")

# Antenna 3
if (antenna_3):
    antenna_3_filepath = os.path.join(stl_path, "antenna_3.stl")
    polyhedrons['antenna_3']  = materialList['antenna'].AddPolyhedronReader(antenna_3_filepath,  priority=5)
    assert(polyhedrons['antenna_3'] .ReadFile(), f"Found file")

# Feed
feed_filepath = os.path.join(stl_path, "feed.stl")
polyhedrons['feed']  = materialList['antenna'].AddPolyhedronReader(feed_filepath,  priority=5)
assert(polyhedrons['feed'] .ReadFile(), f"Found file")

## SUBSTRATE
# 56 mm height, 18 mm width
FR4_filepath = os.path.join(stl_path, "FR4.stl")
polyhedrons['FR4'] = materialList['FR4'].AddPolyhedronReader(FR4_filepath, priority=4)
assert(polyhedrons['FR4'] .ReadFile(), f"Found file")

## AIR
air_filepath = os.path.join(stl_path, "air.stl")
polyhedrons['air'] = materialList['air'].AddPolyhedronReader(air_filepath, priority=3)
assert(polyhedrons['air'].ReadFile(), f"Found file")

## GROUND
gnd_filepath = os.path.join(stl_path, "gnd.stl")
polyhedrons['gnd'] = materialList['gnd'].AddPolyhedronReader(gnd_filepath, priority=3)
assert(polyhedrons['gnd'].ReadFile(), f"Found file")

### * GRID
from CSXCAD.SmoothMeshLines import SmoothMeshLines


'''
Make sure the mesh is 1/rd inside, and 2/3rds outside the PEC boundary
'''
from mesher import find_poly_min_max, add_poly_mesh_pec, add_poly_mesh_boundary, add_poly_mesh_substrate, find_mins_maxs, add_port_mesh

## AIR
mesh_lists_air = add_poly_mesh_boundary(polyhedrons['air'])
mesh.x = np.concatenate((mesh.x, mesh_lists_air[0]))
mesh.y = np.concatenate((mesh.y, mesh_lists_air[1]))
mesh.z = np.concatenate((mesh.z, mesh_lists_air[2]))
print(f"AIR MESH LIST: \n- {[sorted(lst) for lst in mesh_lists_air]}")
find_poly_min_max(polyhedrons['air'])

## SUBSTRATE
mesh_lists_fr4 = add_poly_mesh_substrate(polyhedrons['FR4'], 1/3)
mesh.x = np.concatenate((mesh.x, mesh_lists_fr4[0]))
mesh.y = np.concatenate((mesh.y, mesh_lists_fr4[1]))
mesh.z = np.concatenate((mesh.z, mesh_lists_fr4[2]))
print(f"FR4 MESH LIST: \n- {[sorted(lst) for lst in mesh_lists_fr4]}")
find_poly_min_max(polyhedrons['FR4'])

## ANTENNA
# Antenna 1
if (antenna_1):
    mesh_lists_antenna_1 = add_poly_mesh_pec(polyhedrons['antenna_1'], 1/3, unit=1e-3)
    mesh.x = np.concatenate((mesh.x, mesh_lists_antenna_1[0]))
    mesh.y = np.concatenate((mesh.y, mesh_lists_antenna_1[1]))
    mesh.z = np.concatenate((mesh.z, mesh_lists_antenna_1[2]))
    print(f"mesh_lists_antenna_1: \n- {[sorted(lst) for lst in mesh_lists_antenna_1]}")
    find_poly_min_max(polyhedrons['antenna_1'])

# Antenna 2
if (antenna_2):
    mesh_lists_antenna_2 = add_poly_mesh_pec(polyhedrons['antenna_2'], 1/3, unit=1e-3)
    mesh.x = np.concatenate((mesh.x, mesh_lists_antenna_2[0]))
    mesh.y = np.concatenate((mesh.y, mesh_lists_antenna_2[1]))
    mesh.z = np.concatenate((mesh.z, mesh_lists_antenna_2[2]))
    print(f"mesh_lists_antenna_2: \n- {[sorted(lst) for lst in mesh_lists_antenna_2]}")
    find_poly_min_max(polyhedrons['antenna_2'])

# Antenna 3
if (antenna_3):
    mesh_lists_antenna_3 = add_poly_mesh_pec(polyhedrons['antenna_3'], 1/3, unit=1e-3)
    mesh.x = np.concatenate((mesh.x, mesh_lists_antenna_3[0]))
    mesh.y = np.concatenate((mesh.y, mesh_lists_antenna_3[1]))
    mesh.z = np.concatenate((mesh.z, mesh_lists_antenna_3[2]))
    print(f"mesh_lists_antenna_3: \n- {[sorted(lst) for lst in mesh_lists_antenna_3]}")
    find_poly_min_max(polyhedrons['antenna_3'])

# Antenna feed
mesh_lists_feed = add_poly_mesh_pec(polyhedrons['feed'], 1/3, unit=1e-3)
mesh.x = np.concatenate((mesh.x, mesh_lists_feed[0]))
mesh.y = np.concatenate((mesh.y, mesh_lists_feed[1]))
mesh.z = np.concatenate((mesh.z, mesh_lists_feed[2]))
print(f"mesh_lists_feed: \n- {[sorted(lst) for lst in mesh_lists_feed]}")
find_poly_min_max(polyhedrons['feed'])

# Ground
mesh_lists_gnd = add_poly_mesh_pec(polyhedrons['gnd'], 1/3, unit=1e-3)
mesh.x = np.concatenate((mesh.x, mesh_lists_gnd[0]))
mesh.y = np.concatenate((mesh.y, mesh_lists_gnd[1]))
mesh.z = np.concatenate((mesh.z, mesh_lists_gnd[2]))
print(f"mesh_lists_gnd: \n- {[sorted(lst) for lst in mesh_lists_gnd]}")
find_poly_min_max(polyhedrons['gnd'])

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
from CSXCAD.CSPrimitives import CSPrimPolyhedron, CSPrimPolyhedronReader
## Lumped Port
import stl
lumped_port_filepath = os.path.join(stl_path, "excitation.stl")
lumped_port_mesh =  stl.mesh.Mesh.from_file(lumped_port_filepath)
portin_start, portin_stop = find_mins_maxs(lumped_port_mesh)

mesh_lists_portin = add_port_mesh(portin_start, portin_stop)
mesh.x = np.concatenate((mesh.x, mesh_lists_portin[0]))
mesh.y = np.concatenate((mesh.y, mesh_lists_portin[1]))
mesh.z = np.concatenate((mesh.z, mesh_lists_portin[2]))

print(f"PORTIN mesh_list: {mesh_lists_portin}")


print(f"resolution_U: {res_u}")
print("mesh.x: {mesh.x}\r\n", sorted(mesh.x))
print("mesh.y: {mesh.y}\r\n", sorted(mesh.y))
print("mesh.z: {mesh.z}\r\n", sorted(mesh.z))

mesh.x = SmoothMeshLines(mesh.x, res_u, ratio=1.4)
mesh.y = SmoothMeshLines(mesh.y, res_u, ratio=1.4)
mesh.z = SmoothMeshLines(mesh.z, res_u, ratio=1.4)

print("mesh.x: {mesh.x}\r\n", mesh.x)
print("mesh.y: {mesh.y}\r\n", mesh.y)
print("mesh.z: {mesh.z}\r\n", mesh.z)

openEMS_grid.AddLine('x', mesh.x)
openEMS_grid.AddLine('y', mesh.y)
openEMS_grid.AddLine('z', mesh.z)

print(f"Portin start: {portin_start}, Portin stop: {portin_stop}")

'''
#! Q
Should I make the feed direction larger?
I need the
- the electric field to be generated across the z direction -> So set the excitation direction to "z"
Voltage probe:
- Will integrate the elecgtric field to get the voltage from start -> stop in the excitation direction
- Will be at the center for non-excitation directions (start + stop) / 2, so the center line of where the excitation happens
Current probe:
- Will be at the center in the excitation direction
- Will go from start-> stop in the non-excitation direction
So the current here is integrated from the 2 edges of the port. 
The reason why we only integrate the current along a single line, is because due to the 
way the excitation happens, we can assume certain behaviours in the magnetic field inside the dielectric (certain mode excitations etc..).
This leads us to be able to use this single line-integral to estimate the current.
'''
ports['portin'] = FDTD.AddLumpedPort(port_nr=1, R=feed_R, start=portin_start, stop=portin_stop, p_dir='z', excite=1, priority=6)

#######################################################################################################################################
# DUMPS
#######################################################################################################################################
dumps = {}
# add a nf2ff calc box; size is 3 cells away from MUR boundary condition
start_nf2ff = np.array([mesh.x[4],     mesh.y[4],     mesh.z[4]])
stop_nf2ff  = np.array([mesh.x[-3], mesh.y[-3], mesh.z[-3]])
dumps['nf2ff'] = FDTD.CreateNF2FFBox('nf2ff', start_nf2ff, stop_nf2ff)

# add an electric field dump just above the antenna
start_ebox = np.array([mesh.x[4] , mesh.y[4], portin_start[2]])
stop_ebox  = np.array([mesh.x[-3], mesh.y[-3], portin_start[2]])
dumps['et'] = CSX.AddDump( 'Et_', dump_mode=2 ) # cell interpolated
dumps['et'].AddBox(start_ebox, stop_ebox, priority=0 )
dumps['ht'] = CSX.AddDump(  'Ht_', dump_type=1, dump_mode=2 ) # cell interpolated
dumps['ht'].AddBox(start_ebox, stop_ebox, priority=0 )

#######################################################################################################################################
# RUN
#######################################################################################################################################


### Run the simulation
if sim_enabled:
    CSX_file = os.path.join(Sim_Path, f'{file_name}.xml')
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

freq = np.linspace(f0-fc,f0+fc,501)
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