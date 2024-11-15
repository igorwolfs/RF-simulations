# -*- coding: utf-8 -*-
"""
 Microstrip Notch Filter Tutorial

 Tested with
  - python 3.10
  - openEMS v0.0.35+

 (c) 2016-2023 Thorsten Liebig <thorsten.liebig@gmx.de>

"""
#
# FUNCTION TO GIVE RANGE WITH ENDPOINT INCLUDED arangeWithEndpoint(0,10,2.5) = [0, 2.5, 5, 7.5, 10]
#     returns coordinates in order [theta, r, z]
#
def arangeWithEndpoint(start, stop, step=1, endpoint=True):
	if start == stop:
		return [start]

	arr = np.arange(start, stop, step)
	if endpoint and arr[-1] + step == stop:
		arr = np.concatenate([arr, [stop]])
	return arr


### Import Libraries
import os, tempfile
from pylab import *
import os, tempfile, shutil
import copy
import math
from CSXCAD  import ContinuousStructure
from openEMS import openEMS

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'


## constants
from openEMS.physical_constants import *
unit = 1e-6 # specify everything in um

## prepare simulation folder
currDir = os.getcwd()
file_name = 'MSL_ports_copper_lumped'
Sim_Path = os.path.join(currDir, file_name)
Sim_CSX = 'MSL_copper.xml'
if os.path.exists(Sim_Path):
	shutil.rmtree(Sim_Path)   # clear previous directory
	os.mkdir(Sim_Path)    # create empty simulation folder
     

## setup FDTD parameter & excitation function
max_timesteps = 40000
min_decrement = 1e-10

CSX = ContinuousStructure()
FDTD = openEMS(	EndCriteria=min_decrement)
FDTD.SetCSX(CSX)


#######################################################################################################################################
# BOUNDARY CONDITIONS
#######################################################################################################################################
FDTD.SetBoundaryCond( ['MUR', 'MUR', 'MUR', 'MUR', 'PEC', 'MUR'] )
# FDTD.SetBoundaryCond( ['PEC', 'PEC', 'PEC', 'PEC', 'PEC', 'PEC'] )
# FDTD.SetBoundaryCond( ['PML_8', 'PML_8', 'PML_8', 'PML_8', 'PEC', 'PML_8'] )

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
# EXCITATION sinewave
#######################################################################################################################################
f_max = 7e9
wavelength_max = (C0/f_max)
wavelength_max_u = wavelength_max / unit
FDTD.SetGaussExcite( f_max/2, f_max/2 )

#######################################################################################################################################
# MATERIALS 
#######################################################################################################################################
materialList = {}


## MATERIAL - COPPER
materialList['copper'] = CSX.AddMaterial('copper')
materialList['copper'].SetMaterialProperty(epsilon=1.0, mue=1.0, kappa=56e6, sigma=0.0)
# materialList['copper'] = CSX.AddMetal('copper')

MSL_dz = 36;  # thickness
MSL_dy = 500;  # trace width
MSL_dx = 400e3  # 500 mm
pec_start = [-MSL_dx/2, -MSL_dy/2, -MSL_dz]
pec_end = [MSL_dx/2, MSL_dy/2, 0]
materialList['copper'].AddBox(start=pec_start, stop=pec_end, priority=20)

## MATERIAL - FR4
materialList['FR4'] = CSX.AddMaterial('FR4')
substrate_epr = 4.6
materialList['FR4'].SetMaterialProperty(epsilon=substrate_epr, mue=1.0, kappa=0.0, sigma=0.0)
substrate_thickness = 1.6e3 # 1.6 mm

substrate_start = [-MSL_dx/2, -4*MSL_dy, 0]
substrate_stop  = [MSL_dx/2, 4*MSL_dy, -substrate_thickness]
materialList['FR4'].AddBox(start=substrate_start, stop=substrate_stop, priority=0)

## MATERIAL - AIR
materialList['air'] = CSX.AddMaterial('air')
materialList['air'].SetMaterialProperty(epsilon=1.0, mue=1.0, kappa=0.0, sigma=0.0)

# Only subtract lambda / 4 in case there's no PEC
air_start = [substrate_start[0], substrate_start[1], 0]
# safety of lambda/4 from edge absorption condition
air_stop = [substrate_stop[0], substrate_stop[1], substrate_thickness]
materialList['air'].AddBox(start=air_start, stop=air_stop, priority=0)


## MATERIAL - PML
#! DEFINE HERE FOR KAPPA
#? FOR SOME REASON THE PML DOESN'T REFLECT HERE AS IT DOES IN MSL_S_parameter_check.m
# port2_dx = 50e3
# finalKappa = 1/(port2_dx**2) 	
# finalSigma = finalKappa*MUE0/EPS0
# materialList['fakepml'] = CSX.AddMaterial('fakepml')
# materialList['fakepml'].SetMaterialProperty(kappa=finalKappa, sigma=finalSigma)
# materialList['fakepml'].SetMaterialWeight(epsilon='pow(x-' +str(MSL_dx/2-port2_dx/2) + ',2)')
# materialList['fakepml'].SetMaterialWeight(kappa='pow(x-' +str(MSL_dx/2-port2_dx/2) + ',2)')
# fakepml_start = [MSL_dx/2-port2_dx/2,  -4*MSL_dy,  -substrate_thickness]
# fakepml_stop  = [MSL_dx/2, 4*MSL_dy, substrate_thickness]
# materialList['fakepml'].AddBox(start=fakepml_start, stop=fakepml_stop, priority=10 )

'''
For some reason the dielectric here doesn't absorb, it simply reflects
-> Figure out why.
The problem here seems to be that the port reflects, perhaps this is because the port impedance is a discrete 50 ohms.
So the idea here is we need either 
- to match the port impedance, to make the port non-reflective.
- to remove the port and simply put probes there instead
What happens when removing the port is the energy becomes even larger.
It seems to me that the problem is in fact one that relates to the PML layer at the end
-> Let's try to verify that by simulating PEC boundary conditions everywhere.
The dielectric should normally have a loss tangent since
- epsilon = 4.6
- mu = 1
- kappa = 0
- sigma = 0
tan(delta) = sigma / (omega * epsilon) -> since sigma (resistivity) is 0 there should be no loss and there should be just a waving back and forth
-> Try to add the copper conductor to introduce loss. This doesn't completely bring down the energy to zero
-> Try to add the fakepml to bring down the energy to ß -> This brings down the energy a bit quicker but still doesn't reduce to zero quite as quickly for some reason.
	Seems like this is mostly a reflection issue however
'''

#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################
SIMBOX_START = np.array([substrate_start[0], air_start[1], -substrate_thickness])
SIMBOX_STOP = np.array([substrate_stop[0], air_stop[1], air_stop[2]])

## MAIN GRID
wavelength = (C0/f_max) *  (1/(sqrt(substrate_epr)))
wavelength_u = wavelength / unit

resolution_xyz = np.array([wavelength / 15, wavelength / 15, wavelength / 15])
resolution_u_xyz = resolution_xyz / unit
print(f"RESOLUTION: {resolution_xyz}")
print(f"RESOLUTION: {resolution_u_xyz}")

mesh.x = np.concatenate((mesh.x, arangeWithEndpoint(SIMBOX_START[0], SIMBOX_STOP[0], resolution_u_xyz[0])))
mesh.y = np.concatenate((mesh.y, arangeWithEndpoint(SIMBOX_START[1], SIMBOX_STOP[1], resolution_u_xyz[1])))
mesh.z = np.concatenate((mesh.z, arangeWithEndpoint(SIMBOX_START[2], SIMBOX_STOP[2], resolution_u_xyz[2])))

print(f"mesh_x: {mesh.x}")
print(f"mesh_y: {mesh.y}")
print(f"mesh_z: {mesh.z}")

## COPPER GRID
# * y-copper plane
mesh.y = np.delete(mesh.y, np.argwhere((mesh.y <= -MSL_dy/2) & (mesh.y >= MSL_dy/2)))
# Make sure to have a mesh 1/3rd inside and 2-3rds outside of your conductor mesh
mesh.y = np.concatenate((mesh.y, np.array([-MSL_dy*5/3, -MSL_dy*2/3, MSL_dy/3, MSL_dy*5/3])))

# * z-copper plane
mesh.z = np.delete(mesh.z, np.argwhere((mesh.z >= -MSL_dz*5/3) & (mesh.z <= 2*MSL_dz/3)))
# Make sure to have a mesh 1/3rd inside and 2-3rds outside of your conductor mesh
mesh.z = np.concatenate((mesh.z, np.array([-MSL_dz*5/3, -2*MSL_dz/3, -MSL_dz / 3, 2*MSL_dz/3])))

## DIELECTRIC GRID
mesh.z = np.concatenate((mesh.z, np.array([60.0, 120.0, 200, 300, substrate_thickness])))

####################################################################################
################################# PORTS ############################################
####################################################################################

ports = []
'''
FUNCTION: FDTD.AddMSLPort( 1,  materialList['copper'], port1start, port1stop, 'x', 'z', excite=1, FeedShift=port1_exc_dx, MeasPlaneShift=port1_meas_dx, priority=10)
@param: exc_dir: 'z' -> The excitation direction here is "z", which is the direction of the E-field excitation.
@param: prop_dir: 'x' -> The propagation direction, which is "x" in this case because the direction of propagation is "x".
@param: feed-shift: 10 * resolution -> Shift the port from start by a given distance in drawing units (in the propagation direction), default = 0, ONLY works when ExcitePort is set.
@param: measure plane shift: MSL_length / 3 -> Shifts the measurement plane from start a given distance (in the propagation direction) in drawing units (Default is the midldle of start / stop)
@param: feed_R -> None (default), is the port lumped resistance. By default there is NONE and the port ends in an ABC-absorption boundary condition
'''
# ! TODO: Simply try adding the points here and perform a "SmoothMeshLines"-call on the meshlines

port1_dx = 100e3
port1start = [-MSL_dx/2+port1_dx,          -MSL_dy/2,  substrate_start[2]]
port1stop  = [-MSL_dx/2+port1_dx,  MSL_dy/2,  substrate_stop[2]]
mesh.x = np.concatenate((mesh.x, np.array([-MSL_dx/2+port1_dx, -MSL_dx/2])))
print(f"port: X: ({port1start[0]:.2e}->{port1stop[0]:.2e}), Y:({port1start[1]:.2e}->{port1stop[1]:.2e}), Z:({port1start[2]:.2e}->{port1stop[2]:.2e})")

port2_dx = 100e3
port2_meas_dx = 40e3
port2start = [(MSL_dx/2-port2_dx),          -MSL_dy/2, substrate_start[2]]
port2stop  = [(MSL_dx/2)-port2_dx,  MSL_dy/2,  substrate_stop[2]]
print(f"port: X: ({port2start[0]:.2e}->{port2stop[0]:.2e}), Y:({port2start[1]:.2e}->{port2stop[1]:.2e}), Z:({port2start[2]:.2e}->{port2stop[2]:.2e})")
mesh.x = np.concatenate((mesh.x, np.array([MSL_dx/2-port2_meas_dx])))

## AddLines
openEMS_grid.AddLine('x', mesh.x)
openEMS_grid.AddLine('y', mesh.y)
openEMS_grid.AddLine('z', mesh.z)

'''
FUNCTION: SmoothMeshLines(lines, max_res, ratio=1.5, **kw):
@param: List of mesh lines to be smoothed.
@param: Maximum allowed resolution, resulting mesh will always stay below that value.
@param: Ratio of increase or decrease of neighboring mesh lines.
'''
from CSXCAD.SmoothMeshLines import SmoothMeshLines

# print(f"GRID BEFORE: ")
# print(f"{np.sort(openEMS_grid.GetLines(2))}")
# newgrid = SmoothMeshLines(np.sort(openEMS_grid.GetLines(2)), resolution_u_xyz[0]/5, 1.6)
# print(f"{newgrid}")

print("BEFORE")
print(f"X_Meshlines: {openEMS_grid.GetLines(0)}")
print(f"Y_Meshlines: {openEMS_grid.GetLines(1)}")
print(f"Z_Meshlines: {openEMS_grid.GetLines(2)}")


'''
Choosing gridlines here equal to /5, /5, instead of /2, /2 give a VERY weird result
- It takes much longer for the wave to propagate (maybe because the time-step is in fact smaller?)
It seems like the energy is not decreasing 
-> although it does seem like that in the simulation visualization, but for some reason the dB number doesn't show it.
We're trying to optimize the grid to get the same result as the MSL_S_parameter_check.m matlab file.
- The energy doesn't seem to leave? Maybe it's because the material isn't lossy? Let's simply run with the dE/dt as limit
'''
openEMS_grid.SmoothMeshLines(0, resolution_u_xyz[0], 1.1)
openEMS_grid.SmoothMeshLines(1, resolution_u_xyz[1], 1.1)
openEMS_grid.SmoothMeshLines(2, resolution_u_xyz[2], 1.1)

print("AFTER")
print(f"X_Meshlines: {openEMS_grid.GetLines(0)}")
print(f"Y_Meshlines: {openEMS_grid.GetLines(1)}")
print(f"Z_Meshlines: {openEMS_grid.GetLines(2)}")

feed_R = 0 # ATTEMPT AT PREVENTING REFLECTIONS
portExcitationAmplitude = 4000.0
portDirection = 'z'
ports.append(FDTD.AddLumpedPort( 1, feed_R, port1start, port1stop, 'z', excite=1.0 * portExcitationAmplitude, priority=30))
ports.append(FDTD.AddLumpedPort( 2, feed_R, port2start, port2stop, 'z', priority=30))



####################################################################################
################################# EXCITATION #######################################
####################################################################################


### Run the simulation
CSX_file = os.path.join(Sim_Path, 'notch.xml')

if not os.path.exists(Sim_Path):
    os.mkdir(Sim_Path)

CSX.Write2XML(CSX_file)

from CSXCAD import AppCSXCAD_BIN
os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

####################################################################################
#################################### DUMPS #########################################
####################################################################################

Et = CSX.AddDump('Et', file_type=0)
Et.AddBox(SIMBOX_START, SIMBOX_STOP)

# FDTD.Run(Sim_Path, cleanup=True)
FDTD.Run(Sim_Path, cleanup=True, debug_material=True, debug_pec=True, debug_operator=True, debug_boxes=True, debug_csx=True, verbose=3)


#!############################### POST-PROCESSING #####################################
#######################################################################################
#################################### DISPLAY ##########################################
#######################################################################################

### Post-processing and plotting
f = linspace( 1e6, f_max, 1601 )
for p in ports:
    p.CalcPort( Sim_Path, f, ref_impedance = 50)

'''
S-parameters calculated to a reference impedance of 50 ohms.
- S11: reflected / incoming voltage to port 0
- S21: reflected voltage at port 1 (so b2) / incoming voltage at port 0 (There is no excitation at port 1) 
b1 = S11 * a1 + S21 * a2 -> S11 = b1 / a1 (fraction of power reflected at port 1)
b2 = S22 * a2 + S12 * a1 -> S12 = b2 / a1 (fraction of power transferred from port 2 to port 1)
-> NOTE: S-matrix is symmetric (S21 = S12) only if
- reference impedances are real
- elements contain only reciprocal materials
https://cds.cern.ch/record/1415639/files/p67.pdf
'''


########
# PLOT S-PARAMETERS HERE
s11 = ports[0].uf_ref / ports[0].uf_inc
s21 = ports[1].uf_ref / ports[0].uf_inc

#### RESONANT FREQ CALCULATIONS
MSL_length = (MSL_dx - port2_dx - port1_dx)*unit
i=1
res_freq_list = []
res_freq = (i * 3.0e8) / (2 * MSL_length * math.sqrt(substrate_epr))
while (res_freq < f_max):
	res_freq_list.append(res_freq)
	i += 1
	res_freq = (i * 3.0e8) / (2.0 * MSL_length * math.sqrt(substrate_epr))
res_freq_list = np.array(res_freq_list)
print(f"REESONANT FREQUENCIES: {res_freq_list}")
figure()
plot(f/1e9,20*log10(abs(s11)),'k-',linewidth=2 , label='$S_{11}$')
plot(f/1e9,20*log10(abs(s21)),'r--',linewidth=2 , label='$S_{21}$')
plot(res_freq_list/1e9, np.zeros_like(res_freq_list), 'bo')  # plot x and y using blue circle markers

grid()
legend()
ylabel('S-Parameter (dB)')
xlabel('frequency (GHz)')
ylim([-40, 2])

plt.savefig(os.path.join(Sim_Path, 's_parameter.pdf'))
show()


########
ZL = ports[0].uf_tot / ports[0].if_tot

## Compare analytic and numerical wave-impedance
figure()
plot(f*1e-6,real(ZL), linewidth=2, label='$\Re\{Z_L\}$')
grid()
plot(f*1e-6,imag(ZL),'r--', linewidth=2, label='$\Im\{Z_L\}$')
ylabel('ZL $(\Omega)$')
xlabel(r'frequency (MHz) $\rightarrow$')
legend()
plt.savefig(os.path.join(Sim_Path, 'zl_parameter.pdf'))
show()



#######################################################################################
#################################### COMMENTS #########################################
#######################################################################################

'''
MESH CREATION FOR CONDUCTORS
1. We need to create one general mesh
2. We need to remove the places where there are conductors around "a factor" (let's says 2 or 3*width) of the conductor
3. We need to add a grid there that refines from lambda / 20 to the grid width, to make sure there is at least 1 grid-point within the conductor
	- Create a function that logarithmically (with a factor of n), reduces the grid size from a to b
4. We need to do the same on the other side of the conductor, above, and below the conductor
-> CHeck why SmoothMeshLines doesn't do the job as it is supposed to.
'''

'''
INSTABILITY IN SIMULATIONS
Q?
Maybe the fact that the excitation keeps going has to do with the fact that we have 2 unused primitives?

Most instabilities are due to one of 2 things
### 1. Boundary condition problem
To check whether this is the problem, set all boundary conditions to metal. This should get rid of the boundary condition (PML) instability.
In this case there is still a weird energy contained in the conductor for some reason, no idea why.
The reason for this is (probably)? the PEC that comes with the MSL-port excitation type
-> So probably avoid using the MSL_port with a full thickness PEC since it leads to weird stuff. Try to pinpoint the problem later-on.

### 2. Timestep instability problem
Here you can reduce the courant number.
### SOURCES
https://optics.ansys.com/hc/en-us/articles/11277217507603-Troubleshooting-diverging-simulations-in-FDTD
'''

'''
NOTE: for some reason when just displaying both copper and PEC, the curve does not look the same as in a normal MSL (as in MSL_S_parameter_check.m)

'''