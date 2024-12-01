"""
Goal: 
- simulate an inset-feed antenna resonator at 2.5 GHz.
- add an MSL at 50 ohms to supply the resonator

"""

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
max_timesteps = 30000
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
f0 = 2e9 # center frequency
fc = 1e9 # 20 dB corner frequency

FDTD.SetGaussExcite( f0, fc )


#######################################################################################################################################
# MATERIALS
#######################################################################################################################################
materialList = {}

## CREATE PATCH MATERIAL
'''
Feed patch calculated based on: 
-> https://3g-aerial.biz/en/online-calculations/antenna-calculations/patch-antenna-online-calculator
'''

materialList['patch'] = CSX.AddMetal( 'patch' ) # create a perfect electric conductor (PEC)
patch_dx = 32
patch_dy = 40
patch_dz = 0
patch_dy0 = 1+1+3.5
patch_x0 = 10

## CREATE FEED LINE

'''
Calculated using: https://www.emtalk.com/mscalc.php?er=3.38&h=1.524&h_units_list=hmm&f=2.5&Zo=200&EL=0&Operation=Synthesize&Wa=3.5288393627391&W_units_list=Wmm&La=0&L_units_list=Lmm
WARNING: introducing a length here larger than a few 10 degrees will increase the reflection coefficient dramatically and thus decrease the antenna efficiency
- MSL_dx = 40: the phase-shift for 2.5 GHz is about 180 degrees when it arrives at the feed point. 
-> The entire wave will then simply be reflected
- MSL_dx = 80: the phase-shift is supposed to be 360 degrees so barely any reflections, it seems however not entirely the case. It might also be that lots of energy gets lost somehow.
It seems like MSL_dx = 15 creates the same impedance the patch antenna has when fed at its centre.
-> To accurately guess the numbers require here, the best thing to do would be a parameter sweep, varying 
'''

materialList['mslfeed'] = CSX.AddMetal( 'mslfeed') # Create PEC feed for antenna signal
msl_dx = 5
msl_dy = 3.5
msl_dz = 0

## CREATE GROUND PLANE
materialList['gnd'] = CSX.AddMetal( 'gnd' ) # create a perfect electric conductor (PEC)

## SUBSTRATE
substrate_epsR   = 3.38
substrate_kappa  = 1e-3 * 2 * pi * 2.45e9 * EPS0 * substrate_epsR
materialList['substrate'] = CSX.AddMaterial( 'substrate', epsilon=substrate_epsR, kappa=substrate_kappa)

# patch width (resonant length) in x-direction
# substrate setup
'''
WARNING: the ground plane for a microstrip patch antenna can also be too large.

'''
subs_dx  = 60
subs_dy = 60
subs_dz = 1.524

# size of the simulation box
SimBox = np.array([240, 240, 150])

wavelength_min = (C0/(f0+fc))
wavelength_min_u = wavelength_min / unit
resolution_u = wavelength_min_u / 20

### Generate properties, primitives and mesh-grid
#initialize the mesh with the "air-box" dimensions

mesh.x = np.concatenate((mesh.x, np.array([-SimBox[0]/2, SimBox[0]/2])))
mesh.y = np.concatenate((mesh.y, np.array([-SimBox[1]/2, SimBox[1]/2])))
mesh.z = np.concatenate((mesh.z, np.array([-SimBox[2]/3, SimBox[2]*2/3])))

#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################

##! DEFINING BOXES
start_patch = []
stop_patch = []
# * CREATE PATCH
# upper patch
start_patch.append([-patch_dx/2, -patch_dy/2, subs_dz])
stop_patch.append([ patch_dx/2 , -patch_dy0/2, subs_dz])

# middle patch
start_patch.append([-patch_dx/2+patch_x0, -patch_dy/2, subs_dz])
stop_patch.append([ patch_dx/2 , patch_dy/2, subs_dz])

# lower patch
start_patch.append([-patch_dx/2, patch_dy0/2, subs_dz])
stop_patch.append([ patch_dx/2 , patch_dy/2, subs_dz])

for i in range(3):  
    materialList['patch'].AddBox(priority=10, start=start_patch[i], stop=stop_patch[i]) # add a box-primitive to the metal property 'patch'


# * MSL
# create msl
start_mslfeed = [(patch_x0 - msl_dx) - patch_dx/2, -msl_dy/2, subs_dz]
stop_mslfeed  = [ patch_x0 - patch_dx / 2, msl_dy/2, subs_dz]
materialList['mslfeed'].AddBox(priority=10, start=start_mslfeed, stop=stop_mslfeed) # add a box-primitive to the metal property 'patch'


# create substrate
start_subs = [-subs_dx/2, -subs_dy/2, 0]
stop_subs  = [ subs_dx/2,  subs_dy/2, subs_dz]
materialList['substrate'].AddBox( priority=0, start=start_subs, stop=stop_subs)

# apply the excitation & resist as a current source
feed_dx = -patch_dx/2 # feeding position in x-direction (assume feeding at the edge)
feed_R = 50 # feed resistance

start_port = [start_mslfeed[0] , 0, 0]
stop_port  = [start_mslfeed[0] , 0, subs_dz]
port = FDTD.AddLumpedPort(1, feed_R, start_port, stop_port, 'z', 1.0, priority=5) #, edges2grid='xy')


##! DEFINING GRID
from CSXCAD.SmoothMeshLines import SmoothMeshLines

third_array = np.array([-1/3, 2/3]) * start_mslfeed[1]/2

# Add extra cells for supply MSL
# We probably don't need these thanks to out existing patch meshing
mesh.y = np.concatenate((mesh.y, np.array([start_mslfeed[1], stop_mslfeed[1]]), start_mslfeed[1] - third_array, stop_mslfeed[1] + third_array))

# Add extra cells from lumped port
mesh.x = np.concatenate((mesh.x, np.array([start_port[0]]), start_port[0] + third_array))
mesh.y = np.concatenate((mesh.y, np.array([start_port[1]]), start_port[1] + third_array))

# add extra cells to discretize the substrate thickness
mesh.z = np.concatenate((mesh.z, linspace(0,subs_dz,5)))


# create ground (same size as substrate)
start_gnd = [-subs_dx/2, -subs_dy/2, 0]
stop_gnd = [subs_dx/2, subs_dy/2, 0]
materialList['gnd'].AddBox(start_gnd, stop_gnd, priority=10)

mesh.x = np.concatenate((mesh.x, np.array([start_gnd[0], stop_gnd[0]])))
mesh.y = np.concatenate((mesh.y, np.array([start_gnd[1], stop_gnd[1]])))

# Add patch 
third_array = np.array([-resolution_u / 3, 2 * resolution_u / 3]) / 2

# FDTD.AddEdges2Grid(dirs='xy', properties=materialList['patch'], metal_edge_res=resolution_u/2)
for i in range(3):
    mesh.x = np.concatenate((mesh.x, start_patch[i][0] - third_array, stop_patch[i][0] + third_array))
    mesh.y = np.concatenate((mesh.y, start_patch[i][1] - third_array, stop_patch[i][1] + third_array))


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

# Add the nf2ff recording box
'''
@brief: Creates a near2farfield-box
@start: by default lowest index in the grid +2/+1 (depending on BC, for MUR=2:  BC_size[2*n)
@stop: by defualt highest index in the grid -2/-1 (depending on BC, for MUR=2: -1*BC_size[2*n+1]-1)
@directions / @mirrors: if the boundary is a PMC or PEC scattering in this direction is not considered, and is set to "false" in the directions-array / seen as magnetic / electric mirrors instead.
NOTE: make sure to call this function only after the entire grid is defined.
'''

nf2ff = FDTD.CreateNF2FFBox()

dump_boxes = {}
## define dump boxes
et_start = [mesh.x[0], mesh.y[0], subs_dz]
et_stop  = [mesh.x[-1], mesh.y[-1], subs_dz]
dump_boxes['et'] = CSX.AddDump( 'Et_', dump_mode=2 ) # cell interpolated
dump_boxes['et'].AddBox(et_start, et_stop, priority=0 )
dump_boxes['ht'] = CSX.AddDump(  'Ht_', dump_type=1, dump_mode=2 ) # cell interpolated
dump_boxes['ht'].AddBox(et_start, et_stop, priority=0 )

#######################################################################################################################################
# SIMULATION
#######################################################################################################################################

### CHECKS
lambda_exp_res = 2*patch_dy
if (subs_dz > lambda_exp_res / 2):
    raise ValueError(f"WARNING: dielectric height to large: {subs_dz} antenna wavelength: {lambda_exp_res}")

if (subs_dz < lambda_exp_res / 80):
    raise ValueError(f"WARNING: dielectric height too small {subs_dz} antenna wavelength: {lambda_exp_res}")

if (msl_dx/lambda_exp_res%1 > 0.1) and (msl_dx/lambda_exp_res%1 < 0.9):
    pass
    # raise ValueError(f"WARNING: msl length is {msl_dx} antenna wavelength: {lambda_exp_res}, electric length: {(msl_dx / lambda_exp_res) * 360}")



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

print(f"Expected resonant frequency: {C0 / (sqrt(substrate_epsR)) / (patch_dx * 2)}")
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
