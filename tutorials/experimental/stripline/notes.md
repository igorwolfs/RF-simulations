# Simulation
## Probes
### Voltage probes
The octave-port simulation of the stripline has voltage probes placed above the stripline, and separately below the stripline.

It seems that doing this improves the accuracy of the s-parameter, since there is field above and below, and this way the measurement is more complete.

### Voltage probe dimensions
VERY IMPORTANT: the potential between 2 points is the path-integral of the electric field along any path between the first and last point.

SO: whatever path we pass along the electric field, the orientation of the voltage probe must be such that the voltage values calculated are sensible, i.e.: have the right orientation.

### Current probe dimensions
The current probes have a z-dimension of 0.250 mm given a total height of 0.5 mm in each direction (so dielectric height of 1 mm).
Why would you have the height included here for the current measurement, while this was not done for the current measurement in the MSL-case.

Plotting this current flow showed no difference whatsoever on observed s-parameter, measuring current this way is probably only necessary in case of a 3D conductor with a finite non-zero conductivity.

## Excitation
The octave-port simulation of the stripline has a separate excitation applied above and below the stripline. This allows to more accurately represent the real-world scenario of a wave propagating along the transmission line.