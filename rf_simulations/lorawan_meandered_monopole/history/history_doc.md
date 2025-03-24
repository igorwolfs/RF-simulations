# Notes
## attempt_2
### Change
- Added extra height to ensure the far-field is captured instead of the near-field.

### Next
- Narrow the frequency range.
- Check the impedance along the desired frequency of 868 MHz.
- Match the impedance.
- If the antenna is still off, try a different feed.

## attempt_3
### Change
- Narrowed down the simulation frequency.

### Observations
- There is no resonance happening at 868 MHz; it appears around 950 MHz instead.

### Next
- Increase the grid accuracy in the Z-direction.
- Lengthen the feed-line so the antenna resonates closer to 868 MHz instead of 950 MHz.
- Create a rudimentary cutout of the ground plane in FreeCAD (lengths of the 50 Ω feedline can be found in rf_lna folder).

### Other
##### Effect of meandering on electrical length
Meandering the antenna decreases its electrical length.
The additional capacitance and inductance introduced by the meanders changes the antenna impedance and, thus, its resonance point.

A meandered antenna may not radiate as efficiently as a simple monopole.

#### Matching networks
As shown in source (1), matching two antennas ensures input matching at the desired frequency (e.g., 915 MHz).

A matching circuit has two main purposes:

- Adapt the antenna impedance so that it resonates and appears close to 50 Ω at the desired frequency.
- Adapt the feed impedance to minimize return loss/reflections.

#### Note: 
A low return-loss point does not necessarily guarantee actual antenna resonance; you could be matching a transmission line with a complex impedance.

#### Viewing the gerber file example
- FR4: Thickness: 1.6 mm
- Dielectric constant: 4.2
- Copper traces:
	- 8 mil (≈0.2032 mm) trace width
	- 8 mil (≈0.2032 mm) isolation
- Observed feeds:
	- First feed: 
		- 2.7 mm width
		- 4.2 mm isolation on both sides
		- 15 mm feed length
	- Second feed
		- 0.7 mm width
		- 1.6 mm isolation
		- 5 mm length
Rule: Place the microstrip about 1.5× the substrate height (h) away from the top ground plane.

- (1) https://muehlhaus.com/support/mwo-appnotes/matching_network_loss

## attempt_4
### Change
- Increased the grid density around ground-plane edges and long PEC edges.
- Increased the simulation space in the x, y, and z directions.

### Observations
- The resonance peak appears around 868 MHz, but the real impedance at resonance is high.
- The geometry-based resonance point is good, but we need to match the antenna (since impedance is too high).

### Next
- Check TI application notes on antennas.
- Consult Small Antennas: Miniaturization Techniques & Applications by John L. Volakis et al.

## attempt_5
### Change
- Added an extra meander to the monopole.

### Observations
- The additional meander decreased the resonance frequency (as expected).

## attempt_6
### Change
- Reduced the meandering by one element (anticipating a frequency increase).

### Observations
- Expect the frequency to increase.

### Next
- Increase the distance between meanders.
- Increase the ground-plane size.
	- (Hoping this will reduce the impedance and tune resonance back toward 868 MHz.)

## attempt_7
### Change
- Increased the meandered distance / decrease the meandering density in order to increase the electrical length

### Observations
- The frequency did increase and the impedance decreased.
- Not enough improvement, so we will continue increasing the distance.

### Next
- Increase the distance even more.

## Attempt 8
### Change
- Increased the meandered distance even more to 10 mm

### Observations
- We achieve a pretty good SNR of under -10 dB. 
- Impedance at resonance is between 885 and 1000 ohms.

### Next
- try to resimulate with a feed-impedance of 900 ohms
- check the resonant frequency
- Consider making the antenna shorter to put the resonant frequency in between 868 and 915 MHz (EU and US frequency)

## attempt_9
### Change
- Ran the antenna simulation with a shifted feed impedance.

### Observations
- The impedance plot is “shaky,” likely due to:
	- Too large frequency steps
	- Under-refined meshing (especially around critical areas)
	- Poorly set boundary conditions

Ideally, use “adaptive meshing” and “adaptive frequency sweep” so the mesh refines until the results converge.

### Next
- Check the effect of adding an extra ground plane below the existing one, connecting them with vias.

## attempt_10
### Change
- Added a second ground plane and created a “decent” VIA orientation to stitch them together:
	- Via fence around the perimeter to confine return currents.
	- Grid vias to lower overall ground inductance, especially around the feed and abrupt ground-plane transitions.
	- Used a via spacing < (λ/20), which for LoRaWAN (868 MHz) is approximately 9.23 mm (accounting for √3.5 in the dielectric).

### Observations
Used FreeCAD for meshing:
- Very low simulation time
- Heavy oscillations (indicating poor accuracy)
- Only a single resonance peak detected, likely due to insufficient mesh points around the antenna PEC.

### Next
- Check how the number of timesteps for the excitation signal is calculated.
- Try increasing the mesh size by adding more points in antenna PEC.

### Other
Make sure to use a via spacing of less than lambda / 20.
I case of lorawan that's 300/(868*20 * sqrt(3.5)) m (9.23 mm) apart.
Make sure sensitivite areas (where abrupt changes occur) have a high via-density.

## attempt_11
### Change
Increased the number of grid points in the Z-direction.

### Observations
- The first resonance peak disappeared entirely.
- The second resonance peak shifted to the right (higher frequency).
- Possible that the 868 MHz resonance is removed by the added ground plane.

### Next
- Try using the same grid on the first antenna, check the result
	- If the result is the same, this might be a resonance shift due to the added ground plane.

### Other
- Might it be that the 868 MHz resonance is effectively removed by the additional ground plane?

## attempt_12
### Change
- Manually meshed the monopole using FreeCAD; resonance was indicated.

### Observations
- Because of the high-Q resonance, the results suddenly become “shaky.”
- Possibly an unstable simulation when adding extra grid points.
	- Not fully understood why it becomes unstable.

### Next
Try a finer mesh and see if the resonance point shifts or stabilizes.

## attempt_13
### Change
- Made a more elaborate grid.
- Used the grid-filter function in mesh_checker.py to remove excess grid points.

### Next
- Check the bandwidth of the antenna.
- Try improving bandwidth by widening the radiating antenna traces.

## attempt_14
### Change
- Widened the antenna traces.

### Observations
- Impedance decrease
- Bandwidth widening
- Electrical length reduction

### Next
- Increase the antenna’s physical length to compensate for the reduced electrical length.


## attempt_15
### Change
- Added an extra meander.

### Observations
- The frequency was reduced (as expected).
- A second resonance frequency became apparent (likely related to one of the earlier meanders).

### Next
- Bring the feed out of the ground plane and re-simulate.
- Depending on the new resonance, adapt the geometry (e.g., thicker traces, more distance between traces).


## attempt_16
### Change
- Removed the long feed-line that was part of the ground plane.

### Next
- Increase the distance between meanders to improve impedance.
- Increase the resonance frequency by reducing the antenna size.
	- See if removing the extra meander combined with increasing the distance between meanders kind-of gets you there while reducing the impedance
- Consider adding a feedpoint short to bring the feedpoint impedance closer to 50 Ω.

## attempt_18
### Change
Made the traces thicker.

### Observations
The resonance peak shifted to the left (lower frequency).

### Next
- Try using thinner traces again.
- Expect the antenna’s resonance around 900 MHz with enough bandwidth to cover 868 MHz and 915 MHz.

## attempt_19
### Observations
- Matching a 2000 Ω antenna down to 50 Ω is difficult.
- We want to bring down the antenna’s impedance to increase the bandwidth.

### Next
- Adjust the antenna geometry to lower its impedance before matching.

## attempt_20
### Change
- Added a separate “leg” to the antenna, giving it an inverted-F–like property to reduce feed impedance.
- Ran separate simulations moving the leg back and forth.

### Observations
- Adding a parallel leg to ground changes current/voltage distribution and lowers apparent feed impedance.
- The added leg can shift resonance significantly.

### Other
#### Why does adding a leg reduces feed impedance?
Because you are basically making a parallel connection to ground.

Note that the effect is not a resistive reduction, it is mostly seen as an inductive / capacitive conductive path, where high-frequency currents and voltages travel.

Due to this the current/voltage distribution is changed, which leads to a lower apparent impedance.

#### Effect of extra feed placing
- Closer to the original feed: impedance becomes higher
- FUrther from the original feed: impedance becomes lower

#### Capacitive vs inductive load
A trace is inherently an inductive load. However it might couple capacitively with the nearby feed.

#### Impedance flip (capacitive -> inductive or vice versa)
Depending on the self-resonant frequency, the load introduced might be capacitive or inductive.

The self-resonant frequency of a conductor is where its inductance and capacitance balance out.
- Below SRF: inductive
- Above SRF: capacitive

#### Effect of thickness on the feedline
- Wider trace: lower characteristic impedance
    - Higher shunt capacitance
    - Lower inductnace
    - So higher self-resonant frequency

- If it carries more current when its wider: more inductive

- If it is wider and this leads to more coupling: more capacitive

#### Reduction of resonant frequency
A reduction in resonant frequency means the electrical length is larger.

The structure now adds onto the antenna, it's part of it.


## attempt_21
### Change
- Removed another meander.
- Made the traces thicker to aim for ~50 Ω at resonance.


## attempt_22
### Change
Widened the antenna traces enough to get ≈50 Ω at resonance.

### Observations
It seeems like at a certain wideness of the antenna, the resonance simply drops away, it's not strong enough and the reactance doesn't drop down to zero.
This might be due to modes being present on the antenna, and the antenna now behaving as a patch-like structure instead of an actual meander.
The reason why resonance doesn't occur is always due to a change in capacitance and inductance leading to undoing the resonance frequency that was originally there.

### Next
- Thin the trace again, check the resonance frequency to bring back the resonance
- Try making the antenna even shorter
- Try moving the parallel gnd connection closer to the feed to decrease the antenna impedance even more.


## attempt_23
### Change
- Made the antenna trace thinner again (which increases inductance and reduces capacitance).

### Observations
- The overall inductance increases and capacitance reduces
- The impedance of the antenna becomes larger
- The resonance becomes more pronounced

### Next
Try bringing the antenna closer to ground, see what effect this has.
- Expected is the capacitance will increase.
- The overall electrical length will decrease.
- This happened, however the result was an increase in reactance at resonance, so a nonzero reactance at resonance as a consequence

## attempt_24
### Change
Moved the initial antenna branch closer to the ground plane.

### Observations
- Increased capacitance to ground.
- Resonance is “messed up,” seemingly needing more inductance to compensate.

## attempt_25
### Change
This antenna covers the required resonance. We can always shorten it by cutting in the copper if we want to achieve higher-frequency resonance. The second resonance peak is about 60 ohms, so by matching that peak we can indeed achieve what we want.

### Observations
As always, there is a todo, which in this case is trimming the antenna in simulation, and checking the resonance frequencies when trimming the antenna, as well as putting black lines at specific frequencies if they can be achieved such as the 1.563-1.587 GHz band.

### Next
Trim the antenna in simulation and observe frequency shifts.

## attempt_26
### Change
Applied the excitation at the edge of the ground plane.

### Observations
The resonance became less pronounced.

### Next
Decrease the antenna thickness again to see if the resonance becomes more distinct.

## attempt_27
### Change
Made the structure thinner.

### Observations
Achieved a better impedance characteristic.

### Next
Move the structure closer to the ground plane to see the inverse effect (likely higher impedance, less pronounced resonance).

## attempt_28
### Change
Moved the antenna closer to the ground plane.

### Observations
Worsened the resonance.

### Next
Move the antenna further from the ground plane.
- Previously it was 9 mm + width
- Then it was 7 mm + width (worsened the resonance, reactance didn't go through 0)
- Now let's try 11 mm + width

## attempt_29
### Change
- Increased the distance to 11 mm + width from the ground plane.

### Observations
- The antenna response “looks like something more usable.”

### Next
- Bring the resonance slightly higher by decreasing the antenna’s width or the overall electrical length (e.g., going from 3 mm to 2.5 mm).

## attempt_30
### Change
Reduced the trace width to 2.5 mm.

### Observations
Now for some reason what happened is
- The impedance decrased
- The resonance peak decreased as well

So decreasing the width this was NOT a good move, although expectations were the inductance had to be higher, that seemed to not have been the case. What if we increase the distance between meanders now?

### Next
- Increase the distance between meanders to see if that helps.

## attempt_31
### Change
Increased the spacing between traces (distance between meanders).

### Observations
The resonance peak shifted to the left (lower frequency), consistent with a longer electrical length.

### Next
- Return the antenna to the original width.
- Place the ground plane even farther away (e.g., 14 mm + width) to improve resonance.

## attempt_32
### Change
- Moved the ground plane even farther from the antenna.

### Observations
- The resonance became more pronounced.

### Next
- Shift the resonance to a higher frequency by decreasing the antenna length.

## attempt_33
### Change
- Finalized the antenna design.

### Observations
- The impedance is slightly off at 868 MHz, but the peak is right around the target frequency.
- The bandwidth is fairly wide; it can likely cover a range around 868 MHz.
