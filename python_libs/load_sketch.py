"""
Goal: 
- Attempt to recreate the lorawan 868 MHz antenna with the correct feed-line.
- Change the antenna and the feed-line accordingly in order to produce a correct frequency that in fact fits on the board.
"""


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