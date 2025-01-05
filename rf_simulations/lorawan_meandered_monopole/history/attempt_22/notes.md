# Done
Widened traces with the goal of achieving 50 ohm impedance at resonance. This worked, about 50 ohm is the impedance at resonance.

- Todo: 
    - remove additional meander
    - shorten the x-dimension of the monopole
in order to increase the resonance frequency.

# Observation
- It seeems like at a certain wideness of the antenna, the resonance simply drops away, it's not strong enough and the reactance doesn't drop down to zero.
- This might be due to modes being present on the antenna, and the antenna now behaving as a patch-like structure instead of an actual meander.
- The reason why resonance doesn't occur is always due to a change in capacitance and inductance leading to undoing the resonance frequency that was originally there

# Action
- Thin the trace again, check the resonance frequency to bring back the resonance
- Try making the antenna even shorter
- Try moving the parallel gnd connection closer to the feed to decrease the antenna impedance even more.