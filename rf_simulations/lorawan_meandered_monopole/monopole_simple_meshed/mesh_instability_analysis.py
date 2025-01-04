"""
Goal: 
- Attempt to recreate the lorawan 868 MHz antenna with the correct feed-line.
- Change the antenna and the feed-line accordingly in order to produce a correct frequency that in fact fits on the board.
"""

import sys
from pathlib import Path, PurePath
import os


# Add path to python
pythonpath = PurePath(Path(__file__).parents[3], 'python_libs')
sys.path.append(os.path.abspath(pythonpath))

if not (os.path.isdir(pythonpath)):
      raise SystemError("Folder python_libs not found")

### Import Libraries
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

## Get models
stl_path = os.path.join(currDir, "freecad")
model_files = os.listdir(stl_path)
model_files = [file_ for file_ in model_files if file_.endswith('.stl')]

### FDTD setup
CSX = ContinuousStructure()
## * Limit the simulation to 30k timesteps
## * Define a reduced end criteria of -40dB
max_timesteps = 540000 * 4 * 4 * 3
end_criteria = 1e-4
FDTD = openEMS(NrTS=max_timesteps, EndCriteria=end_criteria)
FDTD.SetCSX(CSX)

###################################F####################################################################################################
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
f0 = 868e6 # center frequency
fc = 300e6 # 20 dB corner frequency


FDTD.SetGaussExcite( f0, fc )

wavelength = C0 / (f0+fc)
wavelength_u = wavelength / unit
res_u = wavelength_u / 20

#######################################################################################################################################
# MATERIALS
#######################################################################################################################################

materialList = {}

## FR4
substrate_epsR   = 3.38
substrate_kappa  = 1e-3 * 2*pi*2.45e9 * EPS0 * substrate_epsR
materialList['FR4'] = CSX.AddMaterial( 'FR4', epsilon=substrate_epsR)#, kappa=substrate_kappa)

## ANTENNA
materialList['monopole'] = CSX.AddMetal('monopole')

## GND
materialList['gnd'] = CSX.AddMetal('gnd')

## AIR
materialList['air'] = CSX.AddMaterial('air')


#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################

### * Boxes
## ANTENNA
# 55 mm height, 16 mm width
polyhedrons = {}
vertex_lists = {}

mifa_filepath = os.path.join(stl_path, "monopole.stl")
polyhedrons['monopole']  = materialList['monopole'].AddPolyhedronReader(mifa_filepath,  priority=5)
assert(polyhedrons['monopole'] .ReadFile(), f"Found file")

vertex_lists['monopole'] = []
for vtx_i in range(polyhedrons['monopole'].GetNumVertices()):
      vtx = polyhedrons['monopole'].GetVertex(vtx_i)
      vertex_lists['monopole'].append(vtx) 

## GND
gnd_filepath = os.path.join(stl_path, "gnd.stl")
polyhedrons['gnd'] = materialList['gnd'].AddPolyhedronReader(gnd_filepath, priority=3)
assert(polyhedrons['gnd'].ReadFile(), f"Found file")

vertex_lists['gnd'] = []
for vtx_i in range(polyhedrons['gnd'].GetNumVertices()):
      vtx = polyhedrons['gnd'].GetVertex(vtx_i)
      vertex_lists['gnd'].append(vtx) 


## SUBSTRATE
# 56 mm height, 18 mm width
FR4_filepath = os.path.join(stl_path, "FR4.stl")
polyhedrons['FR4'] = materialList['FR4'].AddPolyhedronReader(FR4_filepath, priority=4)
assert(polyhedrons['FR4'] .ReadFile(), f"Found file")

vertex_lists['FR4'] = []
for vtx_i in range(polyhedrons['FR4'].GetNumVertices()):
      vtx = polyhedrons['FR4'].GetVertex(vtx_i)
      vertex_lists['FR4'].append(vtx) 

## AIR
air_filepath = os.path.join(stl_path, "air.stl")
polyhedrons['air'] = materialList['air'].AddPolyhedronReader(air_filepath, priority=3)
assert(polyhedrons['air'].ReadFile(), f"Found file")

vertex_lists['air'] = []
for vtx_i in range(polyhedrons['air'].GetNumVertices()):
      vtx = polyhedrons['air'].GetVertex(vtx_i)
      vertex_lists['air'].append(vtx) 

print(vertex_lists['air'])

mesh_0 = np.load(os.path.join(stl_path, "mesh_0.npy"))
mesh_1 = np.load(os.path.join(stl_path, "mesh_1.npy"))
mesh_2 = np.load(os.path.join(stl_path, "mesh_2.npy"))
meshes = [mesh_0, mesh_1, mesh_2]

print(f"mesh:{mesh_0}")
print(f"mesh:{mesh_1}")
print(f"mesh:{mesh_2}")

#! TODO
from mesh_checker import filter_close_coordinates, filter_close_coordinates_gpt

filter_close_coordinates(meshes, polyhedrons)

filter_close_coordinates_gpt(meshes, polyhedrons)