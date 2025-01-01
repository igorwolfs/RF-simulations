# Antenna
For this simulation, we tried adding a ground plane as well as creating a decent VIA orientation stitching together the 2 ground planes

1. Via fence: Around the perimeter, to confine the return currents
2. Grid vias: lowering overall ground inductance.
    - Making sure to stitch around sensitive regions such as the feed.
    - Sensitive areas: areas where there are abrupt changes / transitions in the ground planes.

Make sure to use a via spacing of less than lambda / 20

I case of lorawan that's 300/(868*20 * sqrt(3.5)) m (9.23 mm) apart.