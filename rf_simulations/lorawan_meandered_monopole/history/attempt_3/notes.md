# Done
- Narrowed down the simualtion frequency.
- There is no resonance happening at 868 MHz for some reason. It's happening somewhere at 950 MHz instead.

# TODO
- Increase the grid accuracy in the Z-direction
- Lengthen the feed-line so the antenna actually resonates at 868 MHz instead of 950 MHz
- Start with rudimentary cutout of the ground plane on freecad
    - Lengths of 50 ohm feedline can be found in rf_lna folder

# Effect of meandering on the "electrical length" of the antenna.
It seems like meandering the antenna decreases the electrical length.
The additional capacitance and inductance introduced by the meanders changes the antenna impedance, and thus its resonance point.

e.g, the antenna doesn't radiate as efficiently as it would if it were a simple monopole.

As can be seen in the link in source (1), we simply match the 2 antennas to ensure input matching at 915 MHz.

The purposes of the matching circuit is thus dual
1. It has to adapt the antenna impedance in order to cause resonance at the desired frequency, at which the impedance becomes real (preferably 50 ohms). 
2. It has to adapt the feed impedance to minimize return loss / reflections at the inputs.

Note that it's not necessarily because the return loss is at a low-point, that the antenna resonates. You might be matching with a transmission line which has a complex impedance.

# Viewing the gerber file example
- FR4: 
    - 1.6 mm thickness
    - 4.2 is dielectric constant
- Copper traces:
    - 8 MIL trace width (0.2032 mm)
    - 8 MIL min isolation (0.2032 mm)
What's visible:
- Initial first feed
    - 2.7 mm width
    - 4.2 mm isolation on both sides
    - 15 mm feed length
- Second feed:
    - 0.7 mm width
    - 1.6 mm isolation
    - 5 mm length

Rule is to always place the microstrip about 1.5 times the substrate height h away from the top ground plane.

# Sources
- (1) https://muehlhaus.com/support/mwo-appnotes/matching_network_loss