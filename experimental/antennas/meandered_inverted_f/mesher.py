
from CSXCAD  import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import *

'''
@brief: Function for polyhedrons to mesh 1/3rd inside, and 2/3rds outside.
- factor: factor (in units) that is used in determining the distance between meshes
@description: takes out duplicate (or close duplicates) based on passed tolerance.
@return: Returns a 3 sub-lists, 1 for each sub-coordinate
'''
def add_mesh(polyhedron, factor, tol=np.array([0.1, 0.1, 0.01]), unit=1e-3):
    assert polyhedron.GetNumVertices() > 0, "ERROR: add_mesh didn't find vertices"
    bbox = polyhedron.GetBoundBox()
    coords = [[], [], []]
    
    #! WARNING: check though if the pcb dimensions are indeed in mm before using the meshing
    # Get all coordinates
    for vtx_i in range(polyhedron.GetNumVertices()):
        vtx = polyhedron.GetVertex(vtx_i)
        for i in range(3):
            coords[i].append(vtx[i])

    # Filter out coordinates
    coords_remove = [[], [], []]
    for c_i in range(3):
        for vtx_i in range(len(coords[c_i])):
            if vtx_i in coords_remove[c_i]:
                continue
            for vtx_j in range(vtx_i+1, len(coords[c_i])):
                if vtx_j in coords_remove[c_i]:
                    continue
                if (np.abs(coords[c_i][vtx_i]-coords[c_i][vtx_j])) < tol[c_i]:
                    # print(f"({vtx_i}: {coords[c_i][vtx_i]}, {vtx_j}: {coords[c_i][vtx_j]})")
                    coords_remove[c_i].append(vtx_j)
        
        # print(f"Removing coords")
        coords[c_i] = np.sort(np.delete(np.asarray(coords[c_i]), np.asarray(coords_remove[c_i])))
        # print(f"coords_remove: {coords[c_i]}")

    #! Add 1/3rd inside and 2/3rds outside depending on closest dimensions
    # Check closest point to mesh point i (between i-1 and i+1)
    # add a numpy array 1/3rd inside and 2/3rds times this distance between the 2 closest points.
    mesh_lists = [[], [], []]
    for c_i in range(3):
        for i in range(len(coords[c_i])):
            dist = 0
            if i == 0:
                dist = np.abs(coords[c_i][0]-coords[c_i][1])
            elif i == len(coords[c_i])-1:
                dist = np.abs(coords[c_i][len(coords[c_i])-1]-coords[c_i][len(coords[c_i])-2])
            else:
                dist = min(np.abs(coords[c_i][i] - coords[c_i][i-1]), np.abs(coords[c_i][i] - coords[c_i][i+1]))
            # Get in and outside mesh
            numpy_mesh = np.array(coords[c_i][i]) + np.array([1/3, -1/3]) * dist
            mesh_lists[c_i].append(numpy_mesh)
    mesh_lists = [np.array(mesh_lists[0]).flatten(), np.array(mesh_lists[1]).flatten(), np.array(mesh_lists[2]).flatten()]
    return mesh_lists