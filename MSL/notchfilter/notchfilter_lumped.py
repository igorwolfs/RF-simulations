'''
# * GOAL:
Create a lumped port excited MSL similar to the MSL port excited MSL.
The MSL does NOT have a z-dimension.

# * RESULT:
Success, the S-parameters and impedance are vastly different but within the realm of possibility 
Possible reasons:
- The source and load impedance aren't matched
- Reflections make the signal go back and forth

The MSL port doesn't have this issue, because
- it is continuous while defining excitation only in one place, so there is no change in impedance along it while it is unavoidable in the lumped port
- it has no resistivity by default.
'''


### Import Libraries
import os, tempfile
from pylab import *
import shutil
from CSXCAD  import ContinuousStructure
from openEMS import openEMS

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'


### CONSTANTS
from openEMS.physical_constants import *
unit = 1e-6 # specify everything in um

## SIMULATION FOLDER SETUP
currDir = os.getcwd()
file_name = os.path.basename(__file__).strip('.py')
Plot_Path = os.path.join(currDir, file_name)
Sim_Path = os.path.join(Plot_Path, file_name)
if not (os.path.exists(Plot_Path)):
	os.mkdir(Plot_Path)
	os.mkdir(Sim_Path)
else:
	shutil.rmtree(Sim_Path)
	os.mkdir(Sim_Path)


## setup FDTD parameter & excitation function
CSX = ContinuousStructure()
FDTD = openEMS()
FDTD.SetCSX(CSX)
#######################################################################################################################################
# BOUNDARY CONDITIONS
#######################################################################################################################################
# FDTD.SetBoundaryCond( ['MUR', 'MUR', 'MUR', 'MUR', 'PEC', 'MUR'] )
# FDTD.SetBoundaryCond( ['PEC', 'PEC', 'PEC', 'PEC', 'PEC', 'PEC'] )

FDTD.SetBoundaryCond( ['PML_8', 'PML_8', 'MUR', 'MUR', 'PEC', 'MUR'] )

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
f_max = 7e9
FDTD.SetGaussExcite( f_max/2, f_max/2 )


#######################################################################################################################################
# MATERIALS
#######################################################################################################################################

materialList = {}

## MATERIAL - PEC
#! Use the jlcpcb impedance calculator to determine dimensions here (https://jlcpcb.com/pcb-impedance-calculator)
materialList['PEC'] = CSX.AddMetal( 'PEC' )
MSL_dx = 25e3 # 50 mm
MSL_dy = 156   # 0.156 mm
MSL_dz = 35    # 0.035 mm
stub_dy = 6e3  # 6 mm


## MATERIAL - RO4350B
substrate_epr = 3.66
substrate_thickness = 99 # 0.099 mm
materialList['RO4350B'] = CSX.AddMaterial( 'RO4350B', epsilon=substrate_epr)

wavelength_min = (C0/f_max) *  (1/(sqrt(substrate_epr)))
wavelength_min_u = wavelength_min / unit

#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################
from CSXCAD.SmoothMeshLines import SmoothMeshLines

## PEC Stub Definition in (the XY-plane)
start_pec_stub = [-MSL_dy/2,  MSL_dy/2, substrate_thickness]
stop_pec_stub  = [ MSL_dy/2,  MSL_dy/2+stub_dy, substrate_thickness+MSL_dz]
materialList['PEC'].AddBox(start_pec_stub, stop_pec_stub, priority=10 )

start_pec = [-MSL_dx/2,  -MSL_dy/2, substrate_thickness]
stop_pec  = [ MSL_dx/2,  MSL_dy/2, substrate_thickness+MSL_dz]
materialList['PEC'].AddBox(start_pec, stop_pec, priority=10 )

## DIELECTRIC Definition
subs_start = [-MSL_dx/2, -10*MSL_dy, 0]
subs_stop  = [+MSL_dx/2, +10*MSL_dy+stub_dy, substrate_thickness]
materialList['RO4350B'].AddBox(subs_start, subs_stop )

## Setup Geometry & Mesh
resolution_u = wavelength_min_u / 50 # resolution of lambda/20
## * Do manual meshing X-DIR
third_mesh_xy = array([2*resolution_u/3, -resolution_u/3])/4
# Add 2/3rds x resolution on the outside and 1/3rd x resolution on the inside of the MSL
mesh.x = np.concatenate((mesh.x, np.array([0.0]), MSL_dy/2+third_mesh_xy, -MSL_dy/2-third_mesh_xy))
mesh.x = SmoothMeshLines(mesh.x, resolution_u/4)

# Add X-edges to the simulation
mesh.x = np.concatenate((mesh.x, np.array([-MSL_dx/2, MSL_dx/2])))

## * Do manual meshing Y-DIR
# Add 2/3rds x resolution on the outside and 1/3rd x resolution on the inside of the MSL
mesh.y = np.concatenate((mesh.y, np.array([0.0]), MSL_dy/2+third_mesh_xy, -MSL_dy/2-third_mesh_xy))
mesh.y = SmoothMeshLines(mesh.y, resolution_u/4)
mesh.y = np.concatenate((mesh.y, (MSL_dy/2+stub_dy)+third_mesh_xy))

# Add edges in Y-edges to simulation 
mesh.y = np.concatenate((mesh.y, np.array([-15*MSL_dy, 15*MSL_dy+stub_dy])))
mesh.y = SmoothMeshLines(mesh.y, resolution_u)

# Create 5 points from 0 to substrate_thickness
# 447 is the size here (447 / 38) = 12
# IF the thickness is 36 um, make sure the resolution is small enough (e.g.: 12 um)
print(f"resolution_u: {resolution_u}")
third_mesh_z = array([2*resolution_u/3, -resolution_u/3])/38
mesh.z = np.concatenate((mesh.z, np.array([0.0]), substrate_thickness+MSL_dz+third_mesh_z, substrate_thickness-third_mesh_z))
mesh.z = SmoothMeshLines(mesh.z, resolution_u/38)

mesh.z = np.concatenate((mesh.z, linspace(0, substrate_thickness, 5), np.array([3000])))

# Z2 boundary condition is MUR, 3000 -> 3 mm
mesh.z = np.concatenate((mesh.z, np.array([3000])))
mesh.z = SmoothMeshLines(mesh.z, resolution_u)


#######################################################################################################################################
# PORTS
#######################################################################################################################################

'''
AddLumpedPort
@param: port_number: simply for naming
@param: exc_dir: 'z' -> The excitation direction here is "z", 
@param: feed_R -> The port lumped resistance, can go from 0 to infinity
@param: start, stop: 
	- the entire excitation will be spread out between this start and stop point! So if there is both a dx, dy and dz the excitation will be all along the dx dy AND dz nodes (volumemetric)
	- the direction of the excitation is derived from whether self.stop - self.start is positive or negative in the excitation direction.
	- the entire "resist" is also added along the entire dx, dy and dz
VOLTAGE PROBE: there is 1 probe for voltage, positioned at start = stop = 0.5(start + stop) for the non-excitation direction, and start, stop for the excitation direction
CURRENT PROBE: there's 1 probe for voltage, which is a sheet in the excitation direction, and has the length and the width of the non-excitation directions.
-> Better to have a distributed port, to have a better result for S-parameters than we would have with a lumped port.
'''
## MSL port setup
ports = {}

feed_R = 50

# Increase wave port size
port1_start = [-MSL_dx/2+MSL_dx/2/3, -MSL_dy/2, substrate_thickness]
port1_stop  = [-MSL_dx/2+MSL_dx/2/3,  MSL_dy/2, 0]
mesh.x = np.concatenate((mesh.x, np.array([port1_start[0]])))
mesh.x = SmoothMeshLines(mesh.x, resolution_u)


port2_start = [MSL_dx/2-MSL_dx/2/3 , -MSL_dy/2, substrate_thickness]
port2_stop  = [MSL_dx/2-MSL_dx/2/3 ,  MSL_dy/2, 0]
mesh.x = np.concatenate((mesh.x, np.array([port2_start[0]])))
mesh.x = SmoothMeshLines(mesh.x, resolution_u)


ports['portin'] = FDTD.AddLumpedPort( 1, feed_R, port1_start, port1_stop, 'z', excite=1, priority=10)
ports['portout']  = FDTD.AddLumpedPort( 2, feed_R, port2_start, port2_stop, 'z', priority=10)


openEMS_grid.AddLine('x', mesh.x)
openEMS_grid.AddLine('y', mesh.y)
openEMS_grid.AddLine('z', mesh.z)

#######################################################################################################################################
# PROBES
#######################################################################################################################################

Et = CSX.AddDump('Et', file_type=0, sub_sampling=[2,2,2])
Et.AddBox(np.array(subs_start)*2, np.array(subs_stop)*2)


#######################################################################################################################################
# RUN
#######################################################################################################################################
### Run the simulation
CSX_file = os.path.join(Sim_Path, 'notch.xml')
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
### Run the simulation

f = linspace( 1e6, f_max, 1601 )

ports['portin'].CalcPort( Sim_Path, f, ref_impedance = 50) 
ports['portout'].CalcPort( Sim_Path, f, ref_impedance = 50) 


## S-Parameter Calculations
s11 = ports['portin'].uf_ref / ports['portin'].uf_inc
s21 = ports['portout'].uf_ref / ports['portin'].uf_inc

plot(f/1e9,20*log10(abs(s11)),'k-',linewidth=2 , label='$S_{11}$')
grid()
plot(f/1e9,20*log10(abs(s21)),'r--',linewidth=2 , label='$S_{21}$')
legend()
ylabel('S-Parameter (dB)')
xlabel('frequency (GHz)')
ylim([-40, 2])

plt.savefig(os.path.join(Plot_Path, 's_parameters.pdf'))
show()


## Z (Impedance) calculations for the port
ZL = ports['portin'].uf_tot / ports['portin'].if_tot
figure()
plot(f*1e-6,real(ZL), linewidth=2, label='$\Re\{Z_L\}$')
grid()
plot(f*1e-6,imag(ZL),'r--', linewidth=2, label='$\Im\{Z_L\}$')
ylabel('ZL $(\Omega)$')
xlabel(r'frequency (MHz) $\rightarrow$')
legend()

plt.savefig(os.path.join(Plot_Path, 'zl_parameters.pdf'))

show()