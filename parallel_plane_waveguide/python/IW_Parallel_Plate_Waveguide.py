# -*- coding: utf-8 -*-
"""
 Rectangular Waveguide Tutorial

 Tested with
  - python 3.10
  - openEMS v0.0.35+

 (c) 2015-2023 Thorsten Liebig <thorsten.liebig@gmx.de>

"""

### Import Libraries
import os, tempfile
from pylab import *

from CSXCAD.CSXCAD  import ContinuousStructure
from openEMS import openEMS

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'

### Setup the simulation
Sim_Path = os.path.join(os.getcwd(), 'sinusoidal')
print(f"SIM_PATH: {Sim_Path}")
###############################################################################################
###################################### SET CONSTANTS ###########################################
###############################################################################################
from openEMS.physical_constants import *

unit = 1 # drawing unit in mm, should be passed whenever creating a grid

### FREQUENCY
f0 = 10e6
fc = 10e3

lambda0 = (C0/f0)/unit; # Number of discrete steps for 1 wavelength


mesh_res = [1, 1, 1]
### PLATE DIMENSIONS
plate_x = np.linspace(-10, 10, 21)
plate_y = np.linspace(-10, 10, 21)
plate_z = np.linspace(-10, 30, 41)

###############################################################################################
###################################### INITIALIZE FDTD ########################################
###############################################################################################

### Setup FDTD parameter & excitation function
NrTS_ = 100
FDTD = openEMS(NrTS=NrTS_, EndCriteria=0, OverSampling=50)

#############################################################################################
################################# BOUNDARY CONDITIONS #######################################
#############################################################################################

# boundary conditions
FDTD.SetBoundaryCond(['PMC', 'PMC', 'PEC', 'PEC', 'MUR', 'MUR'])


#####################################################################################
################################# GRID / MESH #######################################
#####################################################################################

csx = ContinuousStructure()
FDTD.SetCSX(csx)

mesh = csx.GetGrid()
mesh.SetDeltaUnit(unit)


mesh.AddLine('x', plate_x)
mesh.AddLine('y', plate_y)
mesh.AddLine('z', plate_z)

#! WARNING: this is a guess
# mesh.SmoothMeshLines('all', (C0 / fc / unit) / 20, 1)
print(mesh)

####################################################################################
################################# EXCITATION #######################################
####################################################################################

FDTD.SetSinusExcite(f0)

'''
It seems like there is something wrong here with the voltage excitation
- Voltage excitations     : 420    (0, 420, 0)
vs
Warning: Unused primitive (type: Box) detected in property: excitation!
- Voltage excitations     : 0      (0, 0, 0)
'''
#! WARNING: IT SEEMS LIKE THE EXCITATION IS NOT ACTUALLY ACTIVE

# apply the excitation & resist as a current source
start = [plate_x[0], plate_y[0], 0]
stop  = [plate_x[-1], plate_y[-1], 0]

csx_excitation = csx.AddExcitation('excitation', 0, [0, 1, 0])
csx_excitation.AddBox(start, stop)

# #? edges2grid?
# feed_R = 0
# port = FDTD.AddLumpedPort(1, feed_R, start, stop, 'y', 1.0, priority=0)#, edges2grid='xy')

####################################################################################
#################################### DUMPS #########################################
####################################################################################

### Define dump box...
start = [plate_x[0], 0, plate_z[0]]
stop  = [plate_x[-1], 0, plate_z[-1]]

Et = csx.AddDump('Et')
Et.AddBox(start, stop)

### Run the simulation
CSX_file = os.path.join(Sim_Path, 'plane_waveguide.xml')
if not os.path.exists(Sim_Path):
    os.mkdir(Sim_Path)


csx.Write2XML(CSX_file)

from optparse import OptionParser
import inspect
results = inspect.getmembers(csx, predicate=inspect.isfunction)
print(results)
os.system(APPCSXCAD_CMD + ' "{}"'.format(CSX_file))
str_cmd = APPCSXCAD_CMD + ' "{}"'.format(CSX_file)
print(str_cmd)

#### CHECK DIMENSIONS
FDTD.Run(Sim_Path, cleanup=True, debug_material=True, debug_pec=True, debug_operator=True, debug_boxes=True, debug_csx=True, verbose=3)

#######################################################################################
#################################### COMMENTS #########################################
#######################################################################################


'''
### EXCITATION
For some reason the excitation is not passed on.
Volt_Count = volt_vIndex[0].size();
vector<unsigned int> volt_vIndex[3];

volt_vIndex[0].push_back(pos[0]);
virtual unsigned int GetNumberOfLines(int ny, bool full=false) const {UNUSED(full);return numLines[ny];}
-> REASON WAS NON-OVERLAPPING BOUNDARIES FOR EXCITATION SOURCE AND GRID
'''