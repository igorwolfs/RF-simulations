# RF-simulations
This repo contains my learning progress in openEMS and related software for RF simulation and visualization.
It makes extensive use of [FreeCAD](https://www.freecad.org/) and [Python Scripting](/python_libs/).

The [rf_simulations](/rf_simulations/)-folder contains various antenna designs, filter designs and other rf-experiments. 

## Simulation Process
Currrently, the process of simulating a structure works as follows.

### Step 1: Design the objects as bodies in FreeCad
- Sketch the shape of the antenna / air / dielectric
- Extrude the shape as required
- Export the bodies as stl-files

### Step 2: Load the shapes into python.
Use the AddPolyhedronReader function in CSXCAD.
e.g.:
```python
stl_path = os.path.join(currDir, "freecad")
materialList = {}
materialList['monopole'] = CSX.AddMetal('monopole')
mifa_filepath = os.path.join(stl_path, "monopole.stl")
polyhedrons = {}
polyhedrons['monopole']  = materialList['monopole'].AddPolyhedronReader(mifa_filepath,  priority=5)
assert(polyhedrons['monopole'] .ReadFile(), f"Found file")
```
### Step 3: Create the OpenEMS mesh
This is the critical part, depending on the type of material and the complexity of the shape use different methods.

### Meshing through Python Libraries
For an air-boundary / simulation boundary:
```python
mesh_lists_air = add_poly_mesh_boundary(polyhedrons['air'], wavelength_u)
mesh.x = np.concatenate((mesh.x, mesh_lists_air[0]))
mesh.y = np.concatenate((mesh.y, mesh_lists_air[1]))
mesh.z = np.concatenate((mesh.z, mesh_lists_air[2]))
print(f"AIR MESH LIST: \n- {[sorted(lst) for lst in mesh_lists_air]}")
find_poly_min_max(polyhedrons['air'])
```

For a substrate boundary: 
```python
mesh_lists_fr4 = add_poly_mesh_substrate(polyhedrons['FR4'], 1/3)
mesh.x = np.concatenate((mesh.x, mesh_lists_fr4[0]))
mesh.y = np.concatenate((mesh.y, mesh_lists_fr4[1]))
mesh.z = np.concatenate((mesh.z, mesh_lists_fr4[2]))
print(f"FR4 MESH LIST: \n- {[sorted(lst) for lst in mesh_lists_fr4]}")
find_poly_min_max(polyhedrons['FR4'])
```
For a conductor (PEC, Metal) boundary:
```python
mesh_lists_monopole = add_poly_mesh_pec(polyhedrons['monopole'], wavelength_u, 1/3, unit=1e-3)
mesh.x = np.concatenate((mesh.x, mesh_lists_monopole[0]))
mesh.y = np.concatenate((mesh.y, mesh_lists_monopole[1]))
mesh.z = np.concatenate((mesh.z, mesh_lists_monopole[2]))
print(f"monopole MESH LIST: \n- {[sorted(lst) for lst in mesh_lists_monopole]}")
find_poly_min_max(polyhedrons['monopole'])
```
### Meshing through Freecad Macro
I wrote [this macro](python_libs/mesh_extraction_macro.py), which allows for creation of a sketch with names (sketch_xmesh, sketch_ymesh, sketch_zmesh) in freecad, and exports the points in the sketch as a .npy file.

Use this mostly for complicated shapes like meandered antennas. 
These files can then be loaded into the simulation script:
```python
mesh_0 = np.load(os.path.join(stl_path, "mesh_0.npy"))
mesh_1 = np.load(os.path.join(stl_path, "mesh_1.npy"))
mesh_2 = np.load(os.path.join(stl_path, "mesh_2.npy"))
```

### Step 4: Add excitation and probes
#### Excitation
Mostly electric field applied from a copper waveguide to a ground plane (i.e. a voltage).

#### Probes
- Far-field probe: make sure the antenna is situated centrally with respect to the far-field box.


## Tips
### FreeCad
- In the next antenna project, try to make the sheet belong to the same part, and try to have multiple bodies belong to that part.
#### Indicating lengths in FreeCad
Do indicate the right length in freecad use

1. Select 2-lengths.
2. Length: length in the normal direction compared to main face
3. Length2: length in the direction parallel but opposite to the normal.

So if you want to have an object of length 2 mm, floating 1 mm from the normal then
- length = 3 mm
- length2 = -1 mm

note that for some annoying reason the length2 can't be 0, so we need to use a very small number here instead

#### Creating VIAS in FreeCad
1. Sketch a single via (hollow cylinder)
2. Open the Draft-tool
3. The "Position" needs to be set to the position where the x, y and z repetition needs to be started from. E.g.: the left/right upper/down most-position.
4. The x/y/z-interval x/y/z needs to be set to the distance between each repetition
5. Use the copy and rotate tool to make multiple copies of the same via-structure and rotate if necessary
6. Make sure to add all of these together inside a single "part"-container
7. Export as STL.


### Meandering
- When meandering the antenna, the impedance increases because there is inductive coupling with meanders (so inductance goes up)
	- An increased ground plane decreases impedance, since it reduces certain parasitics.


## Resources
### Learning FTDT method
Quick overview of EM theory, finite-method code architecture, types of materials and their models, ..:
- https://github.com/john-b-schneider/uFDTD

### Learning about the design of openEMS itself
OpenEMS tutorials:
- https://docs.openems.de/python/openEMS/Tutorials/index.html
FOSDEM19 intro:
- https://archive.fosdem.org/2019/schedule/event/openems/attachments/slides/3367/export/events/attachments/openems/slides/3367/openEMS_FOSDEM19.pdf
- https://av.tib.eu/media/44458
OpenEMS field simulations in Paraview
- https://www.youtube.com/watch?v=XfZS62qvCN4
 
### Nice add-ons
- https://github.com/SiliconLabs/hardware_design_examples/tree/AntennaSimulationWorkbench/examples
Converts HyperLynx to matlab for electromagnetic simulation or PDF for printing.
- https://github.com/koendv/hyp2mat
KiCad PCB files to openEMS models
- https://github.com/jcyrax/pcbmodelgen
Repository containing a high-level Python interface for mesh generation, kicad footprint generation and much more 
- https://github.com/matthuszagh/pyems