"""
Goal: 
- Attempt to recreate the lorawan 868 MHz antenna with the correct feed-line.
- Change the antenna and the feed-line accordingly in order to produce a correct frequency that in fact fits on the board.
"""

###! MACRO FOR GETTING POINTS FROM SKETCH
'''
import numpy as np
doc = App.ActiveDocument
points_list = []

# X_MESH
points_x = []
try:
    for vec in doc.getObjectsByLabel('sketch_xmesh')[0].Geometry:
        points_x.append(vec.StartPoint.x)
        points_x.append(vec.EndPoint.x)
    points_export = np.unique(np.unique(points_x))
except:
	print(f"x-mesh file not detected")

points_list.append(points_x)

# Y_MESH
points_y = []
try:
    for vec in doc.getObjectsByLabel("sketch_ymesh")[0].Geometry:
        points_y.append(vec.StartPoint.y)
        points_y.append(vec.EndPoint.y)
except:
    print(f"y-mesh file not detected")

points_list.append(np.unique(points_y))	

# Z_MESH
points_z = []
try:
    for vec in doc.getObjectsByLabel('sketch_zmesh')[0].Geometry:
        points_z.append(vec.StartPoint.y)
        points_z.append(vec.EndPoint.y)
except:
	print(f"z-mesh file not detected")

points_list.append(np.unique(points_z))

for i in range(3):
    np.save(f"mesh_{i}", points_list[i])
'''


###! TEST IMPORT PYTHON FILES
from pathlib import Path, PurePath
import numpy as np
import os

file_name = Path(__file__).parts[-1].strip(".py")
currDir = Path(__file__).parents[0]
mesh_0 = np.load(os.path.join(currDir, "freecad_monopole_modified", "mesh_0.npy"))
mesh_1 = np.load(os.path.join(currDir, "freecad_monopole_modified", "mesh_1.npy"))
mesh_2 = np.load(os.path.join(currDir, "freecad_monopole_modified", "mesh_2.npy"))

print(f"meshes: {mesh_0} - {mesh_1} - {mesh_2}")