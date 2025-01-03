import numpy as np
doc = App.ActiveDocument
points_list = []

# X_MESH
points_x = []
for vec in doc.getObjectsByLabel('sketch_xmesh')[0].Geometry:
    if (type(vec) == Part.Point):
        points_x.append(vec.X)
    if (type(vec) == Part.LineSegment):
        points_x.append(vec.StartPoint.x)
        points_x.append(vec.EndPoint.x)


points_list.append(np.unique(points_x))

# Y_MESH
points_y = []
for vec in doc.getObjectsByLabel("sketch_ymesh")[0].Geometry:
    if (type(vec) == Part.Point):
        points_y.append(vec.Y)
    if (type(vec) == Part.LineSegment):
        points_y.append(vec.StartPoint.y)
        points_y.append(vec.EndPoint.y)

points_list.append(np.unique(points_y))	

# Z_MESH
points_z = []

for vec in doc.getObjectsByLabel('sketch_zmesh')[0].Geometry:
    if (type(vec) == Part.Point):
        points_z.append(vec.Y)
    if (type(vec) == Part.LineSegment):
        points_z.append(vec.StartPoint.y)
        points_z.append(vec.EndPoint.y)

points_list.append(np.unique(points_z))

for i in range(3):
    np.save(f"mesh_{i}", points_list[i])