# Patch Antenna
## Geometry
### General
A patch antenna is a rectangular copper pour (width W, length L) sitting on top of a dielectric of thickness h.
The dielectric has relative permittivity epsilon_r.

### Hieght
The height must be between lambda > height > lambda / 40, to prevent degraded efficiency.

### Length
The length L (in line with the feed point), determines the resonance frequency.
- fc = c / (2*L*sqrt(epsilon_r))

So L = lambda / 2 to resomate at a frequency with wavelength lamdba.

### Width
The width controls the impedance.
- Larger width:
    - smaller impedance
    - larger bandwidth
    - less space for other stuff on the PCB

The width also influences the radiation pattern (see formulas in source).

### Operating principle
- The bandwidth of a patch antenna is VERY SMALL.
- It operates at 2-4 % lower frequency than designed for.

**Fringing Fields**
- Current at end and start-length is 0, current at the center is maximum.
    - So the current is 0 at the feed point (L=0), which explains the low impedance.
- The inverse is true of the voltage, it is maximum at the end and the start.
    - This leads to fringing at the edges.
    - These fringing fields are responsible for the radiation. They add-up and produce the radiation.
    - A current adds up in phase on th epatch antenna, and gets cancelled by a current in the opposite direction on the ground plane -> This is why an MSL doesn't radiate, BUT a patch antenna does.

**Effect of epsilon_r**
The smaller epsilon_r, the more "bowed" the fields become, the better the radiation.
-> So smaller substrate permittivity improves the radiation.

However, a smaller epsilon_r also makes the wavelength larger, which thus makes you require a larger antenna.

This is opposite to an MSL, where you want the fields to be contained and be as close to a TEM-mode as possible, with as litle radiation as possible.


## Sources
- https://www.antenna-theory.com/antennas/patches/antenna.php
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

# Questions
## Why does the surface current boundary condition count?
Isn't this boundary condition only valid for PEC's? Isn't that an idealization? Wasn't that a thing which was only valid for PEC's. Don't you ignore the E and B-field parallel to the conductor?
