# Goal
The goal here is to simulate the basic TI lorawan-antenna example, so that it fits on the board, and do the appropriate 50 ohm impedance matching for it.

# Implement the antenna on the RF-LNA board.
- Create a footprint that looks like the antenna.
- Add a connector on the top side.
- Create the feed-line from the connector towards the antenna.
- Add vias through the antenna.

# Antenna project-FreeCad tips
In the next antenna project, try to make the sheet belong to the same part, and try to have multiple bodies belong to that part.

# Meandering 
When meandering the antenna, the impedance increases because there is
- inductive coupling with meanders (so inductance goes up)

An increased ground plane decreases impedance, since it reduces certain parasitics.