# Antenna
For this simulation, we tried adding a ground plane as well as creating a decent VIA orientation stitching together the 2 ground planes

1. Via fence: Around the perimeter, to confine the return currents
2. Grid vias: lowering overall ground inductance.
    - Making sure to stitch around sensitive regions such as the feed.
    - Sensitive areas: areas where there are abrupt changes / transitions in the ground planes.

Make sure to use a via spacing of less than lambda / 20

I case of lorawan that's 300/(868*20 * sqrt(3.5)) m (9.23 mm) apart.

## Meshing
Used freecad for meshing here, this resulted in an extremely low simulation duration, but pretty heavy oscillations indicating a bad simulation accuracy. On top of that only a single resonance peak was detected (second one), probably because lack of points around the antenna PEC.

Try increasing the meshsize by adding more points in freecad (especially around the antenna) and check the simulation.

# TODO
Check how the amount of timesteps for the excitation signal are calculated.