# Simulation

## Fake-PML
The fake-PML here has 
- kappa increasing from 0 to finalKappa, in quadratic fashion.


### Conductivity / Sigma
Conductivity: sigma increasing from 0 to finalSigma, in quadratic fashion.
The higher the conductivity, the more electric current flows.
A perfect conductor has a conductivity of infinity, which means the charges are only present on the outside of the conductor, and there is no electric field inside of the conductor.

**Conductive loss**

A conductivity which is
1. nonzero (zero: means there is no current flow since resistivity is infinite). 
2. non-infinite (infinite: means there is zero resistivity so no loss).

Leads to ohmic losses in a medium. Note that there are many other mechanisms for energy loss in EM wave propagation.

### Loss tangent / Kappa
A parameter mostly used in simulations, calculated from epsilon (electric permittivity) and mu (magnetic permeability) to dampen waves smoothly.

It is not in fact a "Physical"-parameter, more like a function used to scale the permittivity and permeability in such a way as to 
1. introduce EM-loss into the material
2. match the impedance of the main domain to avoid reflections.

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

### Current probe orientation
Make sure the current probe always has the right weight / orientation (so a weight of +1 for an input port, and a weight of -1 for an output port).

## End conditions
When no end conditions are passed, the signal increases to infinity.
So make sure to always add a number of timesteps, high enough to fulfill the simulation, and low enough to make sure the simulation doesn't diverge.

One of the reasons this happens might be because there are not enough energy-dissipating mechanisms present in the simulation.

### How to choose the end condition
Check when the simulation's MSL-energy level becomes pretty uniform, and make sure to stop the simulation at that point. Another option is to run the simulation once to check when the energy drops to its lowest point and then run it again until that point.

## S-Parameter calculation
For S-parameter calculation examples, chack the msl_s_param.py file. Important is that most of the field is contained in the quasi TEM-mode between the copper strip and the copper plate, so that's where the probes should be placed.

It's tough to measure the field above since it gets distorted and is also not the mode through which you transport the energy.

# TODO
## Boundary conditions
### Edge fringe fields
Dive deeper into why boundary conditions lead to field fringin at the edges, and how to solve it
- Perhaps increasing the resolution at the edges will solve this problem?
- Perhaps using different boundary conditions will solve this problem?
- Perhaps moving the excitation source will solve the problem

### Uniform lighting up of the MSL when being excited
