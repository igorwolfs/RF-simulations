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
Sim_Path = os.path.join(os.getcwd(), 'sinusoidalghz')

###############################################################################################
###################################### SET CONSTANTS ###########################################
###############################################################################################
from openEMS.physical_constants import *

unit = 1e-2 # drawing unit in mm, should be passed whenever creating a grid

### FREQUENCY
f_start = 1e6
f0 = 1.5e9
f_stop = 2e9

lambda0 = np.ones(3) * (C0/f0) # Wavelength in meter
print(f"Wavelength: {lambda0} in m")
lambda0_u = lambda0 / unit # Wavelength in "units"
print(f"Wavelength: {lambda0_u} times {unit} needed for one wavelength")

mesh_res_min = lambda0 / 30.0 # Make sure there are 30 mesh-steps per wavelength
mesh_res_max = lambda0 / 20.0 # Make sure there are 30 mesh-steps per wavelength

print(f"Ideal mesh resolution range [{mesh_res_min[0]:.4f} -> {mesh_res_max[0]:.4f}]")

### PLATE DIMENSIONS (since 20 times 1e-2 needed for 1 wavelength, and unit is 1e-2)

plate_x = np.linspace(-20, 20, 41) * unit
plate_y = np.linspace(-20, 20, 41) * unit
plate_z = np.linspace(-20, 60, 81) * unit

print(f"plate_x: {plate_x}")
print(f"plate_y: {plate_y}")
print(f"plate_z: {plate_z}")

###############################################################################################
###################################### INITIALIZE FDTD ########################################
###############################################################################################

### Setup FDTD parameter & excitation function
NrTS_ = 600 # Number of timesteps
nyq_oversampling = 50 # Times the nyquist sampling rate we'll be sampling
FDTD = openEMS(NrTS=NrTS_, EndCriteria=0, OverSampling=nyq_oversampling)

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

####################################################################################
################################# EXCITATION #######################################
####################################################################################

FDTD.SetSinusExcite(f0)

### apply the excitation & resist as a current source
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


os.system(APPCSXCAD_CMD + ' "{}"'.format(CSX_file))
str_cmd = APPCSXCAD_CMD + ' "{}"'.format(CSX_file)

#### CHECK DIMENSIONS
FDTD.Run(Sim_Path, cleanup=True, verbose=3, debug_material=True, debug_pec=True, debug_operator=True, debug_boxes=True, debug_csx=True)

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

QUESTION:
- How is the excitation signal applied to the grid?
    I can see a series of voltages that are generated
    I do not know however which signal gets added to what EC (computational cell)
'''