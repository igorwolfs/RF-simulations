### Import Libraries
import os, tempfile
from pylab import *

from CSXCAD  import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import *

import shutil

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'
print_vertices = False
print_bbox = False

### CONSTANTS
from openEMS.physical_constants import *
unit = 1e-3 # specify everything in um


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
            
## Get models
stl_path = os.path.join(currDir, "freecad")
model_files = os.listdir(stl_path)
model_files = [file_ for file_ in model_files if file_.endswith('.stl')]


### FDTD setup
CSX = ContinuousStructure()
## * Limit the simulation to 30k timesteps
## * Define a reduced end criteria of -40dB
max_timesteps = 60000
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
# MATERIALS
#######################################################################################################################################

materialList = {}

## ANTENNA
materialList['ifa'] = CSX.AddMetal('ifa')

## Test CSPrimPolyhedronReader -> child class of CSPrimPolyhedron
from CSXCAD.CSPrimitives import CSPrimitives
print(f"model_files: {model_files}")
reader = materialList['ifa'].AddPolyhedronReader(os.path.join(stl_path, model_files[0]))
assert(reader.ReadFile(), f"Found file {os.path.join(stl_path, model_files[0])}")

print(f"GetNumVertices: {reader.GetNumVertices()}")
print(f"GetNumFaces: {reader.GetNumFaces()}")
print(f"Primitive bounding box: ")

if print_bbox:
	bbox = reader.GetBoundBox()
	print(f"x: ({bbox[0][0]}->{bbox[1][0]})", end=", ")
	print(f"y: ({bbox[0][1]}->{bbox[1][1]})",  end=", ")
	print(f"x: ({bbox[0][2]}->{bbox[1][2]})")


if print_vertices:
	print("Vertices: ")
	for i in range(reader.GetNumVertices()):
		print(f"v{i}: {reader.GetVertex(i)}")

from mesher import add_mesh
mesh_lists = add_mesh(reader, 0, unit=1e-3)
print(f"mesh_lists: {mesh_lists}")


#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################

# Antenna
mesh.x = np.concatenate((mesh.x, mesh_lists[0]))
mesh.y = np.concatenate((mesh.y, mesh_lists[1]))
mesh.z = np.concatenate((mesh.z, mesh_lists[2]))

print("mesh.x: {mesh.x}\r\n", mesh.x)
print("mesh.y: {mesh.y}\r\n", mesh.y)
print("mesh.z: {mesh.z}\r\n", mesh.z)


openEMS_grid.AddLine('x', mesh.x)
openEMS_grid.AddLine('y', mesh.y)
openEMS_grid.AddLine('z', mesh.z)

CSX_file = os.path.join(Sim_Path, f'{file_name}.xml')
CSX.Write2XML(CSX_file)
