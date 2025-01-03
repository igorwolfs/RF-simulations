# Antenna

Antenna simulation run with a shifted feed impedance.

# Notes
The impedance plot here is pretty shaky, these are artefacts of the simulator due to
- Too large frequency hops
- under-refined meshing, especially around critical areas
- badly set boundary conditions

In principle, you need to have some-kind of "adaptive mesh" / "adaptive frequency sweep"-feature that keeps refining the mesh until there is no more significant change in the result.

# TODO
Check the effect of adding an extra ground plane below the existing one and connecting them with vias.

