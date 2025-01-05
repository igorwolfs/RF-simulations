# Antenna
- Adding separate leg to the antenna to give it an inverted-F like impedance (a.k.a. reduction in impedance) compared to the original design.
- We are doing separate run here to see what happens when we move the leg back and forth
- It seems like the resonant frequency significantly changes when adding a leg.

### Why adding a leg reduces feed impedance?

Because you are basically making a parallel connection to ground.

Note that the effect is not a resistive reduction, it is mostly seen as an inductive / capacitive conductive path, where high-frequency currents and voltages travel.

Due to this the current/voltage distribution is changed, which leads to a lower apparent impedance.

## Effect of extra feed placing
- Closer to the original feed: impedance becomes higher
- FUrther from the original feed: impedance becomes lower

## Capacitive vs inductive load
A trace is inherently an inductive load. However it might couple capacitively with the nearby feed.

## Impedance flip (capacitive -> inductive or vice versa)
Depending on the self-resonant frequency, the load introduced might be capacitive or inductive.

The self-resonant frequency of a conductor is where its inductance and capacitance balance out.
- Below SRF: inductive
- Above SRF: capacitive

## Effect of thickness on the feedline
- Wider trace: lower characteristic impedance
    - Higher shunt capacitance
    - Lower inductnace
    - So higher self-resonant frequency

- If it carries more current when its wider: more inductive

- If it is wider and this leads to more coupling: more capacitive

## Reduction of resonant frequency
A reduction in resonant frequency means the electrical length is larger.

The structure now adds onto the antenna, it's part of it.