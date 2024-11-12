# -*- coding: utf-8 -*-
"""
 Microstrip Notch Filter Tutorial

 Tested with
  - python 3.10
  - openEMS v0.0.35+

 (c) 2016-2023 Thorsten Liebig <thorsten.liebig@gmx.de>

"""

### Import Libraries
import os, tempfile
from pylab import *
import os, tempfile, shutil
import copy

from CSXCAD  import ContinuousStructure
from openEMS import openEMS

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'


## constants
from openEMS.physical_constants import *
unit = 1e-6 # specify everything in um

## prepare simulation folder
currDir = os.getcwd()
Sim_Path = os.path.join(currDir, 'MSL_copper')
Sim_CSX = 'MSL_copper.xml'
if os.path.exists(Sim_Path):
	shutil.rmtree(Sim_Path)   # clear previous directory
	os.mkdir(Sim_Path)    # create empty simulation folder
     

## setup FDTD parameter & excitation function
max_timesteps = 100000
min_decrement = 1e-5

CSX = ContinuousStructure()
FDTD = openEMS()
FDTD.SetCSX(CSX)


#######################################################################################################################################
# BOUNDARY CONDITIONS
#######################################################################################################################################
FDTD.SetBoundaryCond( ['PML_8', 'PML_8', 'MUR', 'MUR', 'PEC', 'MUR'] )

#######################################################################################################################################
# COORDINATE SYSTEM
#######################################################################################################################################

mesh = CSX.GetGrid()
mesh.SetDeltaUnit(unit)
# mesh_x = np.array([])
# mesh_y = np.array([])
# mesh_z = np.array([])



#######################################################################################################################################
# EXCITATION sinewave
#######################################################################################################################################
f_max = 7e9
safety = 2
wavelength_max = (C0/f_max) * safety

FDTD.SetGaussExcite( f_max/2, f_max/2 )

#######################################################################################################################################
# MATERIALS 
#######################################################################################################################################
materialList = {}


## MATERIAL - COPPER
materialList['copper'] = CSX.AddMaterial('copper')
materialList['copper'].SetMaterialProperty(epsilon=1.0, mue=1.0, kappa=56e6, sigma=0.0)

MSL_dz = 36;  # thickness
MSL_dy = 500;  # trace width
MSL_dx = 200e3  # 500 mm

## MATERIAL - FR4
materialList['FR4'] = CSX.AddMaterial('FR4')
substrate_epr = 4.6
materialList['FR4'].SetMaterialProperty(epsilon=4.6, mue=1.0, kappa=0.0, sigma=0.0)
substrate_thickness = 1.6e3 # 1.6 mm

substrate_start = [-MSL_dx, -2*MSL_dy, 0]
substrate_stop  = [MSL_dx, 2*MSL_dy, -substrate_thickness]
materialList['FR4'].AddBox(substrate_start, substrate_stop )

## MATERIAL - AIR
materialList['air'] = CSX.AddMaterial('air')
materialList['air'].SetMaterialProperty(epsilon=1.0, mue=1.0, kappa=0.0, sigma=0.0)

air_start = copy.deepcopy(substrate_start)
# safety of lambda/4 from edge absorption condition
air_stop = copy.deepcopy(substrate_stop)
air_stop[2] = wavelength_max/4
#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################
SIMBOX_START = np.array([-MSL_dx/2, substrate_start[1], -substrate_thickness])
SIMBOX_STOP = np.array([MSL_dx/2, substrate_stop[1], air_stop[2]])
## MAIN GRID
wavelength = (C0/f_max) *  (1/(sqrt(substrate_epr)))
wavelength_u = wavelength / unit
resolution_xyz = np.array([wavelength_u / 50, wavelength_u/50, wavelength_u/50])

mesh.AddLine('x', [SIMBOX_START[0], SIMBOX_STOP[0]])
mesh.SmoothMeshLines('x', resolution_xyz[0])

mesh.AddLine('y', [SIMBOX_START[1], SIMBOX_STOP[1]])
mesh.SmoothMeshLines('y', resolution_xyz[1])

mesh.AddLine('z', [SIMBOX_START[2], SIMBOX_STOP[2]])
mesh.SmoothMeshLines('z', resolution_xyz[2])

## COPPER GRID


## DIELECTRIC GRID



####################################################################################
################################# PORTS ############################################
####################################################################################

ports = []
'''
NOTE: 
@param: exc_dir: 'z' -> The excitation direction here is "z", which is the direction of the E-field excitation.
@param: prop_dir: 'x' -> The propagation direction, which is "x" in this case because the direction of propagation is "x".
@param: feed-shift: 10 * resolution -> Shift the port from start by a given distance in drawing units (in the propagation direction), default = 0, ONLY works when ExcitePort is set.
@param: measure plane shift: MSL_length / 3 -> Shifts the measurement plane from start a given distance (in the propagation direction) in drawing units (Default is the midldle of start / stop)
@param: feed_R -> None (default), is the port lumped resistance. By default there is NONE and the port ends in an ABC-absorption boundary condition
'''
port1_dx = 50e3
port1_exc_dx = 30e3
port1_meas_dx = 40e3
port1start = [-MSL_dx/2,          -MSL_dy/2,  substrate_start[2]]
port1stop  = [-MSL_dx/2+port1_dx,  MSL_dy/2,  substrate_stop[2]]
ports.append(FDTD.AddMSLPort( 1,  materialList['copper'], port1start, port1stop, 'x', 'z', excite=1, FeedShift=port1_exc_dx, MeasPlaneShift=port1_meas_dx, priority=10))


port2_dx = 50e3
port2_meas_dx = 40e3
port2start = [(MSL_dx/2),          -MSL_dy/2, substrate_start[2]]
port2stop  = [(MSL_dx/2)-port2_dx,  MSL_dy/2,  substrate_stop[2]]
ports.append(FDTD.AddMSLPort( 2, materialList['copper'], port2start, port2stop, 'x', 'z', MeasPlaneShift=port2_meas_dx, priority=10))

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

Et = CSX.AddDump('Et', file_type=0, sub_sampling=[2,2,2])
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

s11 = ports[0].uf_ref / ports[0].uf_inc
s21 = ports[1].uf_ref / ports[0].uf_inc

plot(f/1e9,20*log10(abs(s11)),'k-',linewidth=2 , label='$S_{11}$')
grid()
plot(f/1e9,20*log10(abs(s21)),'r--',linewidth=2 , label='$S_{21}$')
legend()
ylabel('S-Parameter (dB)')
xlabel('frequency (GHz)')
ylim([-40, 2])

show()


#######################################################################################
#################################### COMMENTS #########################################
#######################################################################################

'''
QUESTION 1:
- Why are the field values NaN here? Is it because there is no impedance?
'''