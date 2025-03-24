# Lorawan Meandered Monopole

This repository contains simulations data used for tuning an 868 MHz meandered monopole antenna. The kicad-schematics can be found in my [RF-lna-project](https://github.com/igorwolfs/RF-lna-project/tree/main/kicad)-repo.

The antenna design itself was losely based on the DN024 antenna by TI.

## Goal
- Design an antenna that would resonate at 868 MHz, without requiring much matching, that could be used for LoRa-communication.
- Gain a feel of what effects monopole resonance and impedance
	- Adding meanders
	- Decreasing / Increasing width
	- Decreasing / Increasing length
	- Adding stubs

## Design

The full design history with all the simulations can be found inside [this folder](history/).

Not all simulations were saved, the noteworthy ones were saved in a subfolder, containing the simulation data, and a "notes.md" data guessing the reason for the current results, and detailing changes for the next simulation.

- For attempt_1-attempt_4, no relevant files were saved except for the s-parameter and impedance curves.
- Starting from attempt_5, the electric and magnetic field simulations are available. They can be viewed through the (opensource) [paraview](https://www.paraview.org/) software package.

### attempt_5

## Note
OpenEMS is far from ideal for antenna simulations, since it doesn't have basic built-in equations for antennas design, an interactive CAD software, and (most importantly) the possibility to iterate over a range of values for a parameter (e.g.: antenna length / thickness / width / material).