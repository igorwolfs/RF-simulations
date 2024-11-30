# Patch Antenna


# Near-field to Far field transform
## General idea
Far-away from the source, field components are approximately spherical waves. So higher-order terms can be neglected.
-> Only the transversal field components (theta and phi) stay (spherical coordinate system).

So we
1. Define a bounding box around our radiation source
2. Calculate the surface currents on that boundary box based on the formulas
    * Js =  n x H (Electric surface current)
    * Ms =  n x E (Magnetic surface current)
3. We transform these surface currents back into a spherical-coordinate-based electric and magnetic field, with a normal and a tangential direction.
4. We calculate the far field approximation by multiplying this radial component with exp(-k*m*r) / r, assuming the far-field reduces with a factor 1/r.

## Distant-independent radiation pattern.
Once we have obtained the radiation pattern at the surface in polar coordinates, we can approximate the far-field pattern through:
E_far(theta, phi) = E_pattern(theta, phi) * exp(-i*k*r) / r

### Sources:
Thorough analysis:
- https://eecs.wsu.edu/~schneidj/ufdtd/chap14.pdf
Calculating the far-field radial vector based on the surface currents:
- https://space.mit.edu/RADIO/CST_online/mergedProjects/3D/special_postpr/special_postpr_pp_farfield.htm
