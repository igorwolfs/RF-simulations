# Goal
The goal is to simulate a meandered monopole antenna for GNSS receiving. We'll later print this meandered monopole onto a PCB, together with matching circuit and connector, and attempt to decode gnss messages using the Pluto-SDR.


# Theory
Central idea: fold the antenna back and forth to make the antenna shorter.
As a consequence however, often radiation efficiency decreases. The radiation profile changes, and the bandwidth decreases.

## Basic monopole simulation

## Possible meanders
Simply using rectangular edges.

# Simulation
## Observing resonance
If not observing resonance at (or around) the desired frequency (a.k.a. the imaginary )
## Antenna length
Whenever using a dielectric, realize that part of your waves are contained within the dielectric, and another part is not.
So in order to determine the correct resonance length you should take some kind of weighted average between 
- Your dielectric permittivity
- The air permittivity


e.g.: $eps_{eff} = \frac{(eps_{r} + 1)}{2}$

# Simulations
## Antenna length
Apparently when simply using the approximation of: $eps_{eff} = \frac{(eps_{r} + 1)}{2}$ the antenna length is not decent, and the resonance frequency turns out to be too high (so the wavelength / antenna length too short). This is probably due to the fact that the electric field contained inside the dielectric is smaller relatively speaking compared to the field in air.

Stackup is the following:
- L1: CU: 0.035 mm
- prepreg: 0.2104 mm prepreg (dielectric 4.4)
- L2: 0.0152 mm copper
- Core: 1.065 mm (dielectric: 4.6)
- L3: 0.0152 mm copper
- Prepreg: 7628, RC 49 %, 0.2104 mm
- L4: CU: 0.035 mm

To get the required epsilon we need to take 0.1 times the dielectric permittivity + 0.9 times the permittivity of air

# Resources:
How to meander antennas + why there are meandered this way:
- https://www.qsl.net/kk4obi/Meander%20Dipole.html
- http://www.gsm-modem.de/M2M/m2m-faq/embedded-antenna-bluetooth-gps-gnss/

