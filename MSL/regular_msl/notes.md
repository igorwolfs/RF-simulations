# Simulation
## Boundary Conditions
The example simulation was done with boundary conditions

- length: x1 -> x2: 'MUR'
- width: y1 -> y2: 'PMC' 
- height: z1: 'PEC' z2: 'PMC' 

### PMC
A PMC boundary reflects the tangential component of the magnetic field.
It forces the electric field to be tangential to the boundary.

**Z2, Y1, Y2 PMC Boundary**

With this boundary condition we represent infinite open air. So the field-lines curl around the microstrip.

### PEC
**Using MUR/PML_8 instead of PMC**

Using absorptive boundaries has the same effect as using a PMC.

## Meshing

### Conductor boundary meshing
We see in "structured.py" that for some reason only meshing is done at the conductor boundary, not inside the conductor, and it seems to work.

However:
- The copper t is 1 mm, the substrate t is 10 mm (ratio of 10 to 1)
- Typical copper t is 35 um, substrate t is 1570 (ratio of 44 to 1)

**Conclusion**
> So maybe the smaller ratio leads to less stringent meshing requirements. OR maybe the width to height ratio is just too large for this simulation. \
=> (Formula Restrictions: 0.1 < w/h < 3.0)

## Probes
### Probe locations
**Dual voltage probes**

2 voltage probes are defined, ut1 and ut2.
- ut1: is positioned at the 
    - x: index closest to MSL-length / 2 (296.7)
    - y: conductor center,
    - z: conductor boundary with dielectric
- ut2: (y and z same as ut1), x is positioned at the mesh index of ut1 + 1 (x:303.3)

**Current probe**

it1 current probe is defined
- x: (start == stop) positioned between ut1 and ut2, so (ut1_x + ut2_x) / 2
- y: edges of the MSL + a bit extra (dy / 2 for that node)
    - start: index closest to one edge of the MSL
    - stop: index closest to the other edge of the MSL
- z: Same as y, around the edges + a bit extra (dz / 2 for that node)


**Shifting current and voltage probes**

H-field and E-fields are not computed at the same place in FDTD, they are staggered with respect to each other in the Yee-grid.
In order to compute the voltage at the same location as the current you need to do this kind of staggering.

**Excitation vs Probe location**

Make sure to shift the excitation far enough away from the measurement probes to ensure
- The excitation signal has enough time to settle into its steady state. There might be spurious modes or non-uniform fields appearing due to the excitation which we don't want to measure.
- There might be reflections interacting with the excitation, which might leads to weird voltage signals.
