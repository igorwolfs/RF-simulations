# Simulation
## Probes
### Voltage probes
The octave-port simulation of the stripline has voltage probes placed above the stripline, and separately below the stripline.
When doing this for a stripline, shouldn't one do the same thing for an MSL and the air?

### Current probe dimensions
The current probes have a z-dimension of 0.250 mm given a total height of 0.5 mm in each direction (so dielectric height of 1 mm).
Why would you have the height included here for the current measurement, while this was not done for the current measurement in the MSL-case?

-> Normally, there is only current flow on the SURFACE of a PEC, so calculating current using a box encircling dielectric doesn't make sense, because there is no current flowing in the dielectric given the dielectric's conductivity is 0 by default

## Excitation
The octave-port simulation of the stripline has a separate excitation applied above and below the stripline.
