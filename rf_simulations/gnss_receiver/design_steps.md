# GPS Patch antenna design
## Notes
### Excitation frequency
Make sure to choose the right frequency to sweep, the Gaussian Pulse excitation is calculated in "excitation.cpp", "CalcGaussianPulseExcitation".

Since a gaussian pulse is shaped as: $A*exp(-(t / {\sqrt{2} * \sigma_{t})^{2}}$. 
Its fourier transform is $A*\sqrt{2*\pi*\sigma_{t}^{2}} * exp(-(2*\pi*\sigma_{t}*f)^2)$. So spectral density is a gaussian as well.

Thus by choosing the excitation frequency / cutoff frequency too far from the actual frequency to be observed, the energy might become too low to actually be representative of the result.
