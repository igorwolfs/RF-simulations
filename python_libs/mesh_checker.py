import numpy as np

coordstring = ["x", "y", "z"]


def filter_close_coordinates(mesh_lists, polyhedrons, min_meshdiff=[0.1, 0.1, 0.01], min_dist=[0.01, 0.01, 0.01]):
    # Ensure input meshes are sorted and unique
    mesh_lists_c = [sorted(set(mesh)) for mesh in mesh_lists]
    print("mesh_lists_c")
    for i in range(3):
        print(len(mesh_lists_c[i]))
    # Filter out points in the mesh that are too close to each other
    mesh_lists_filtered = []
    for i in range(3):
        filtered_mesh = [mesh_lists_c[i][0]]  # Start with the first element
        for point in mesh_lists_c[i][1:]:
            if (point - filtered_mesh[-1]) >= min_meshdiff[i]:
                filtered_mesh.append(point)
        mesh_lists_filtered.append(filtered_mesh)

    print("mesh_lists_filtered")
    for i in range(3):
        print(len(mesh_lists_filtered[i]))
    # Extract vertices from polyhedrons
    vertex_coords = [[], [], []]
    for poly in polyhedrons.values():
        for vtx_i in range(poly.GetNumVertices()):
            vertex = poly.GetVertex(vtx_i)
            for i in range(3):
                vertex_coords[i].append(vertex[i])
    vertex_coords = [np.unique(coords) for coords in vertex_coords]

    # Filter mesh coordinates too close to polyhedron boundaries
    mesh_lists_new = []
    for i in range(3):
        new_mesh = []
        for point in mesh_lists_filtered[i]:
            if np.min(np.abs(vertex_coords[i] - point)) > min_dist[i]:
                new_mesh.append(point)
        mesh_lists_new.append(new_mesh)

    print("mesh_lists_new")
    for i in range(3):
        print(len(mesh_lists_new[i]))
    return mesh_lists_new


def refine_mesh(mesh_lists, polyhedrons, min_meshdiff=[0.1, 0.1, 0.01], min_dist=[0.01, 0.01, 0.01], additional_points=[1, 1, 1], max_ratio=1.5, start=[None, None, None], stop=[None, None, None]):
    """
    Refines the input mesh by adding additional points where the ratio of distances
    between consecutive points exceeds max_ratio, with preference for points within a specified range.

    Parameters:
        mesh_lists (list of lists): Input mesh lists [x_mesh, y_mesh, z_mesh].
        polyhedrons (dict): Dictionary of polyhedron objects.
        min_meshdiff (list): Minimum distance between consecutive mesh points.
        min_dist (list): Minimum distance between a polyhedron point and a mesh point.
        additional_points (list of int): Number of points to add between mesh points for each dimension.
        max_ratio (float): Ratio threshold for adding points.
        start (list of floats): Starting coordinates for preferred mesh placement [x_start, y_start, z_start].
        stop (list of floats): Ending coordinates for preferred mesh placement [x_stop, y_stop, z_stop].

    Returns:
        refined_mesh_lists (list of lists): Refined mesh lists [x_mesh, y_mesh, z_mesh].
    """
    # Ensure input meshes are sorted and unique
    mesh_lists_c = [sorted(set(mesh)) for mesh in mesh_lists]

    refined_mesh_lists = []

    for i in range(3):
        current_mesh = mesh_lists_c[i]
        refined_mesh = []

        # Adjust the range based on start and stop preferences
        mesh_start = start[i] if start[i] is not None else current_mesh[0]
        mesh_stop = stop[i] if stop[i] is not None else current_mesh[-1]

        # Filter points within the specified range
        points_in_range = [point for point in current_mesh if mesh_start <= point <= mesh_stop]

        # Add additional points for refinement
        points_to_add = additional_points[i]
        evenly_distributed_mesh = []
        for j in range(len(points_in_range) - 1):
            p1 = points_in_range[j]
            p2 = points_in_range[j + 1]
            evenly_distributed_mesh.append(p1)

            dist = p2 - p1
            if dist > 0 and dist / (min_meshdiff[i]) > max_ratio:
                new_points = np.linspace(p1, p2, points_to_add + 2)[1:-1]
                evenly_distributed_mesh.extend(new_points)

        # Add the last point in range
        if points_in_range:
            evenly_distributed_mesh.append(points_in_range[-1])

        refined_mesh_lists.append(sorted(evenly_distributed_mesh))

    return refined_mesh_lists

# Example usage:
mesh_lists = [
    [0.0, 0.2, 0.5, 0.7],
    [0.0, 0.3, 0.6, 0.9],
    [0.0, 0.25, 0.5, 0.75]
]
polyhedrons = {}  # Assuming this would be filled with valid polyhedron data
refined_mesh = refine_mesh(
    mesh_lists, 
    polyhedrons, 
    additional_points=[2, 3, 4], 
    max_ratio=1.5, 
    start=[0.1, 0.2, 0.1], 
    stop=[0.6, 0.8, 0.6]
)
print(refined_mesh)
