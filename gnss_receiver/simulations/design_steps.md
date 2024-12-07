# GPS Patch antenna design
## Notes
### Excitation frequency
Make sure to choose the right frequency to sweep, the Gaussian Pulse excitation is calculated in "excitation.cpp", "CalcGaussianPulseExcitation".

Since a gaussian pulse is shaped as: $A*exp(-(t / {\sqrt{2} * \sigma_{t})^{2}}$. 
Its fourier transform is $A*\sqrt{2*\pi*\sigma_{t}^{2}} * exp(-(2*\pi*\sigma_{t}*f)^2)$. So spectral density is a gaussian as well.

Thus by choosing the excitation frequency / cutoff frequency too far from the actual frequency to be observed, the energy might become too low to actually be representative of the result.


## Antenna design, impedance matching and delay input
- You can move the reference (so shift the impedance phase) using the nanoVNA, to make sure the coax doesn't count as impedance
- You can add a COAX and solder the end COAX to 2 pads.
- You can always shorten the antenna by cuting the trace
- Check how matching circuit elements were positioned. 0 ohm and 2 other components for example.
https://www.youtube.com/watch?v=rbXq0ZwjETo

## Check this one
https://www.youtube.com/watch?v=x1m8G8MAeUQ

## Important
- Find the right soldering coax
- Find good examples where you can see how the matching elements were put there for later soldering and adaptation.