
from CSXCAD  import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import *

'''
@brief: Function for polyhedrons to mesh 1/3rd inside, and 2/3rds outside.
- factor: factor (in units) that is used in determining the distance between meshes
@description: takes out duplicate (or close duplicates) based on passed tolerance.
@return: Returns a 3 sub-lists, 1 for each sub-coordinate
'''
def add_poly_mesh_pec(polyhedron, factor=1/3, tol=np.array([0.1, 0.1, 0.01]), unit=1e-3):
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

    '''
    WARNING:
        - Meshing here happens based on the closest coordinate in the same dimension 
        - Suboptimal (1/3rd, 2/3rds preferred)
        - Might not work with round shapes (would take 1/3rd in and 1/3rd out of the tolerance, since it skips points that are on the tolerance)
            - Check how they are described before using it on round shapes
    '''
    # Check closest point to mesh point i (between i-1 and i+1)
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
            numpy_mesh = np.array(coords[c_i][i]) + np.array([factor, -factor]) * dist
            mesh_lists[c_i].append(numpy_mesh)
    mesh_lists = [np.array(mesh_lists[0]).flatten(), np.array(mesh_lists[1]).flatten(), np.array(mesh_lists[2]).flatten()]
    return mesh_lists


def add_poly_mesh_boundary(polyhedron, factor=1/3, unit=0.2):
    assert polyhedron.GetNumVertices() > 0, "ERROR: add_mesh didn't find vertices"
    bbox = polyhedron.GetBoundBox()
    return [np.array([bbox[0][0], bbox[1][0]]), np.array([bbox[0][1], bbox[1][1]]), np.array([bbox[0][2], bbox[1][2]])]


def add_poly_mesh_substrate(polyhedron, factor=1/3, unit=[1.0, 1.0, 0.1], interval=[2, 2, 0.5]):
    assert polyhedron.GetNumVertices() > 0, "ERROR: add_mesh didn't find vertices"
    bbox = polyhedron.GetBoundBox()

    mesh_lists = []
    for c_i in range(3):
        # mesh_c_i_start = bbox[0][c_i] + np.array([-unit[c_i], unit[c_i], 0])
        # mesh_c_i_stop = bbox[1][c_i] + np.array([-unit[c_i], unit[c_i], 0])
        # mesh_c_i = np.concatenate((mesh_c_i_start, mesh_c_i_stop))
        mesh_c_i = np.arange(bbox[0][c_i], bbox[1][c_i], interval[c_i])
        mesh_lists.append(mesh_c_i)

    return mesh_lists


def find_poly_min_max(polyhedron):
    bbox = polyhedron.GetBoundBox()
    print(f"- X: ({np.min(bbox[0][0]), np.max(bbox[1][0])})")
    print(f"- Y: ({np.min(bbox[0][1]), np.max(bbox[1][1])})")
    print(f"- Z: ({np.min(bbox[0][2]), np.max(bbox[1][2])})")

###########################################################################################
################### PYTHON-STL LIBRARY FUNCTIONS ##########################################
###########################################################################################

def add_port_mesh(port_start, port_stop, factor=1/3, unit=0.2):
    mesh_lists = []
    for c_i in range(3):
        # In case start and stop are the same, filter out the var
        unique_mesh = np.unique(np.array([port_start[c_i], port_stop[c_i]]))
        # If they are the same: make sure to set small grid before and after depending on factor

        # If they are different, set a grid 1/3rd off of the difference of the port
        if (len(unique_mesh) == 1):
            mesh_c_i = unique_mesh + np.array([unit, -unit, 0])
        elif (len(unique_mesh) == 2):
            dist = np.abs(unique_mesh[1] - unique_mesh[0])
            #! WARNING: this will lead to small meshes for small ports -> make sure to account for this when it happens
            meshstart_c_i = unique_mesh[0] + np.array([factor, -factor, 0])*dist
            meshstop_c_i = unique_mesh[1] + np.array([factor, -factor, 0])*dist
            mesh_c_i = np.concatenate((meshstart_c_i, meshstop_c_i))
        else:
            print("ERROR")
            return -1
        mesh_lists.append(mesh_c_i.flatten())
    return mesh_lists

def find_mins_maxs(obj):
    minx = obj.x.min()
    maxx = obj.x.max()
    miny = obj.y.min()
    maxy = obj.y.max()
    minz = obj.z.min()
    maxz = obj.z.max()
    return np.array([minx, miny, minz]), np.array([maxx, maxy, maxz])
