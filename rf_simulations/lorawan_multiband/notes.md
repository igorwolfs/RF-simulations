# LoRaWan Multi-band antenna
We will try to recreate this lorawan multi-band antenna and perform some practical tests with it to verify the results from the paper.

## Stackup
Our stackup:
- L1: CU: 0.035 mm
- prepreg: 0.2104 mm prepreg
- L2: 0.0152 mm copper
- Core: 1.065 mm
- L3: 0.0152 mm copper
- Prepreg: 7628, RC 49 %, 0.2104 mm
- L4: CU: 0.035 mm
So:
- height: 1.4858 mm


The FR4 used for prototyping was:
- length: 80 mm
- width: 50 mm
- height: 1.6 mm

### How was the stackup in the paper?

## Simulation
Steps
1. Create the 2 antennas as separate sketches, as well as the ground plane and the feed-line.
2. Create thte separate "switching piece" in between the antennas so you can simulate that too.
3. Make sure the relevant dielectric height is taken into account.
4. Find a way to integrate the ground plane into the whole simulation
    - Add the excitation somehow to the PCB the via-structure which conducts to the actual ground plane.

## KiCad
In order to simulate this antenna in KiCad, we need to
1. Have the 2 antenna-parts separately as a footprint.
2. Have a way to integrate the switching diodes into the design.
3. Draw the feed-line from the bottom all the way up to the antenna
4. Find a way to connect the feedling to the bottom of the PCB
    - front of the connector connected to a transmission line conencted to the antennas
    - sides of the connector connected to the bottom ground plane through vias.

## Diode switches

Finding the relevant diode switches.
The pin diode switches used in the paper are the following: BAR50-02V (LCSC: C4468002)

### Working principle
- DC reverse bias, they block.
- DC forward bias: they work.

So we need to actually connect wires / traces to the diodes to make sure they conduct as required.

The options at hand
1. Simply connect inputs on both sides of the diodes with very high inductors.
    - Pro: easy
    - Con: not sure if the inductance will be high enough, hard to simulate? Check if lumped element simulations are in fact that hard.
2. Connect the inputs with shielded wires to a DC voltage directly.

NOTE: 
- A problem here is that whenever there will be forward biasing, the forward voltage will need to be about 1.1 V at least (Vf)
SO: 
- We will need a bias-T between the rf transmitter and the antenna input, in order to forward-bias the antenna
OR
- We need an AC blocking capacitor in between the coax feed and the antenna when we apply a high voltage to the antenna
    - This is probabably a better option, it might introduce some impedance matching issues though.


### Mistake in the drawing
- There is a mistake in the drawing, the inner vertical line is supposed to be
    - 38 mm
    - The upper line: 2 mm
    - The lower line: 4 mm
    - The lower gap: 1 mm
    So the total length here shuold be: 45 mm, the indication says "43 mm" however.
    Assume that the length is 43, and deduce everything from that.

# FreeCad
### Issue when sketching
Make sure to when sketching don't create overlapping figures e.g.: overlapping squares when drawing an rectangular angle.