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