# Dipole types
A linear conductor is resonant with any integer multiple of half a wavelength of the respective frequency.


## Full wave
The length of the dipole is equal to a full wavelength.
The current distribution is 0 at the center, so the impedance there becomes infinity.


## Half-wave
The length of the dipole antenna is half a wavelength. The current is maximal at the center (a.k.a. feed point).

Expression for radiated power in a half-wave dipole:
-> https://en.wikipedia.org/wiki/Dipole_antenna

The impedance is about 73 ohm for a half-wave dipole.

### Feeding from a COAX
Sometimes people feed a dipole from a coax, connecting the inner part of the coax to one branch, and the outer to another.
The reason for this is that the outer shield has the opposite wave-form to the inner one.

The magnetic and electric fields created due to the current running through the inner wire induce an opposite current on the outer shield, which keeps the fields inside the wire.

### Dipole antenna issue fixing

So why is my dipole antenna impedance not equal to 75 ohms? There are some options
1. The feed is done wrong: There's a pretty long feed and
    - The current going in is measured halfway through the feed
    - The voltage drop is measured across the feed
2. The dipole geometry is bad
    - Not probably, since it's not that complicated, simply half wave
3. The excitation is bad
    - Maybe instead of defining opposite signals of excitation, we do something completely different
    - This might in fact be true -> Since we are taking a gaussian and reversing the direction of excitation, maybe this doesn't equal directly to providing a balanced input



### Checking the balance of the excitation
# Dipole Simulation
The issue at the first simulation was probably that either side of the dipole weren't connected to a + and a -. They were simply fed with the same wave-form at both sides.

## Antenna input impedance calculation
The best way to 

## Balanced vs unbalanced signals
For some antennas (such as a dipole) you need to provide a balanced signal. A balanced signal is when 2 wires are used to carry it, the signal itself and the signal in opposite polarity. 

### Noise in balanced signals
This often has pretty good noise cancellation properties, since when signal is transported inside the same wire in a balanced way, both polarities pick up the same noise level, when they are thus summed up in the end their noise cancels out.

# TODO:
- Simulate a dipole:
    - Example designs: https://www.edaboard.com/threads/printed-log-periodic-dipole-array-optimization-openems-and-balanced-unbalanced-matching.409846/
- You need to turn the unbalanced feedline into a balanced feedline using a balun
    - So you also need to print a balun.
    - Balun examples: https://www.uniteng.com/neildocs/references/Balun_Design_odyseus_nildram_co_uk.pdf
    - Maybe keep this for a later stage, since balun designs might already get you into some wild territory.
    - Start with a basic RF amp + some inverted F antenna.

- Take an antenna
- Start working with Pluto-SDR
- Buy the required equipment

## Creating the dipole
1. Create a pad that can work as a supply port
2. Create a dipole antenna footprint
3. Import into kicad
