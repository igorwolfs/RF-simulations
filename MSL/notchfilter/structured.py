'''
Basic example taken from theliebig
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

## prepare simulation folder
currDir = os.getcwd()
file_name = 'structured'
Plot_Path = os.path.join(currDir, file_name)
Sim_Path = os.path.join(Plot_Path, file_name)
Sim_CSX = 'MSL_copper.xml'
if os.path.exists(Plot_Path):
	shutil.rmtree(Plot_Path)   # clear previous directory
	os.mkdir(Plot_Path)    # create empty simulation folder
	os.mkdir(Sim_Path)    # create empty simulation folder



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
materialList['PEC'] = CSX.AddMetal( 'PEC' )
MSL_dx = 100000 # 5 cm
MSL_dy = 600 # 0.6 mm
stub_dy = 12e3 # 12 mm


## MATERIAL - RO4350B
substrate_epr = 3.66
substrate_thickness = 254
materialList['RO4350B'] = CSX.AddMaterial( 'RO4350B', epsilon=substrate_epr)

wavelength_min = (C0/f_max) *  (1/(sqrt(substrate_epr)))
wavelength_min_u = wavelength_min / unit

#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################
from CSXCAD.SmoothMeshLines import SmoothMeshLines
## PEC Stub Definition in (the XY-plane)
start = [-MSL_dy/2,  MSL_dy/2, substrate_thickness]
stop  = [ MSL_dy/2,  MSL_dy/2+stub_dy, substrate_thickness]
materialList['PEC'].AddBox(start, stop, priority=10 )


## DIELECTRIC Definition
subs_start = [-MSL_dx/2, -15*MSL_dy, 0]
subs_stop  = [+MSL_dx/2, +15*MSL_dy+stub_dy, substrate_thickness]
materialList['RO4350B'].AddBox(subs_start, subs_stop )


## Setup Geometry & Mesh
resolution_u = wavelength_min_u / 50 # resolution of lambda/50
## * Do manual meshing X-DIR 
# The division by 4 here comes from the fact tha the smoothing happens on resolution / 4 -> so there the resolution is reduced even more.
third_mesh = array([2*resolution_u/3, -resolution_u/3])/4
# Add 2/3rds x resolution on the outside and 1/3rd x resolution on the inside of the MSL
# We add 2/3rds x MSL_dy here since the stub in the y-direction requires fine-grained dy-edges
mesh.x = np.concatenate((mesh.x, np.array([0.0]), MSL_dy/2+third_mesh, -MSL_dy/2-third_mesh))
mesh.x = SmoothMeshLines(mesh.x, resolution_u/4)

# Add X-edges to the simulation
mesh.x = np.concatenate((mesh.x, np.array([-MSL_dx/2, MSL_dx/2])))
# mesh.x = SmoothMeshLines(mesh.x, resolution_u)
mesh.x = SmoothMeshLines(mesh.x, resolution_u)

## * Do manual meshing Y-DIR
# Add 2/3rds x resolution on the outside and 1/3rd x resolution on the inside of the MSL
mesh.y = np.concatenate((mesh.y, np.array([0.0]), MSL_dy/2+third_mesh, -MSL_dy/2-third_mesh))
mesh.y = SmoothMeshLines(mesh.y, resolution_u/4)
mesh.y = np.concatenate((mesh.y, (MSL_dy/2+stub_dy)+third_mesh))

# Add edges in Y-edges to simulation 
mesh.y = np.concatenate((mesh.y, np.array([-15*MSL_dy, 15*MSL_dy+stub_dy])))
mesh.y = SmoothMeshLines(mesh.y, resolution_u)

# Create 5 points from 0 to substrate_thickness
mesh.z = np.concatenate((mesh.z, linspace(0, substrate_thickness, 5)))

# Z2 boundary condition is MUR, 3000 -> 3 mm
mesh.z = np.concatenate((mesh.z, np.array([3000])))
mesh.z = SmoothMeshLines(mesh.z, resolution_u)

openEMS_grid.AddLine('x', mesh.x)
openEMS_grid.AddLine('y', mesh.y)
openEMS_grid.AddLine('z', mesh.z)

#######################################################################################################################################
# PORTS
#######################################################################################################################################

'''
AddMSLPort
@param: exc_dir: 'z' -> The excitation direction here is "z", which is the direction of the E-field excitation.
@param: prop_dir: 'x' -> The propagation direction, which is "x" in this case because the direction of propagation is "x".
@param: feed-shift: 10 * resolution -> Shift the port from start by a given distance in drawing units (in the propagation direction), default = 0, ONLY works when ExcitePort is set.
@param: measure plane shift: MSL_dx / 3 -> Shifts the measurement plane from start a given distance (in the propagation direction) in drawing units (Default is the midldle of start / stop)
@param: feed_R -> None (default), is the port lumped resistance. By default there is NONE

PROBES: There 3 probes for the voltage, 2 for the current.
-> Better to have a distributed port, to have a better result for S-parameters than we would have with a lumped port.
FEED RESISTANCE: Assumed to be zero when no parameter is passed. If a parameter is passed a reflection might occur since it changes the impedance.
'''
## MSL port setup
ports = {}

portstart = [ -MSL_dx/2, -MSL_dy/2, substrate_thickness]
portstop  = [ 0,  MSL_dy/2, 0]
ports['portin'] = FDTD.AddMSLPort( 1,  materialList['PEC'], portstart, portstop, 'x', 'z', excite=-1, FeedShift=10*resolution_u, MeasPlaneShift=MSL_dx/2/3, priority=10)

portstart = [MSL_dx/2, -MSL_dy/2, substrate_thickness]
portstop  = [0         ,  MSL_dy/2, 0]
ports['portout']  = FDTD.AddMSLPort( 2, materialList['PEC'], portstart, portstop, 'x', 'z', MeasPlaneShift=MSL_dx/2/3, priority=10)


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
Z_ref = 50
ports['portin'].CalcPort( Sim_Path, f, ref_impedance = Z_ref) 
ports['portout'].CalcPort( Sim_Path, f, ref_impedance = Z_ref) 


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