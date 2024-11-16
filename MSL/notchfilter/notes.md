# Simulation
## Meshing
### Meshing ratio around PEC
It is VERY IMPORTANT to always have a mesh line of:
- 2*resolution / 3 outside of the conductor
- resolution/3 inside the conductor

## Ports
### Lumped port
**Lumped port resistance**

When defining a lumped port, make sure there's a gridline in the x-direction (propagation direction), otherwise the excitation won't get registered.

NOTE: When defining a lumped port with impedance 0, you are basically defining a PEC. PEC's have an impedance 

> DO NOT choose a lumped port impedance of 0, unless it's in the propagation plane, since this would mean a PEC plane. It would then go on to fully reflect all signals.
Choosing the feed impedance to infinity minimizes any reflections.

**Lumped Port Size**

In case where the lumped port is too big, it seems that the excitation doesn't go away, and you simply get a very big circle indicating a high electric field around the place where excitation was applied.
The EM wave shows similar behaviour though, as if not affected by this huge red circular chunk of energy.

Because of bad port dimensions, regions are excited which don't correspond to the MSL's intended transmission mode. These hot-spots don't propagate which leads to the lingering electric field.

> A lumped port excitation must only be applied 
> - orthogonal to the propagation direction
> - in a plane connecting the 2 conductors (the microstrip and conducting plane), WITHOUT overlapping with one of the conductors.
> - It's width should be a bit bigger than the signal line width.



### Source
https://innovationspace.ansys.com/courses/wp-content/uploads/sites/5/2021/07/HFSS_GS_2020R2_EN_LE6_Port_Basics.pdf

# Theory
## TEM-Modes
TEM mode is a mode where electric and magnetic field lines are restricted to directions normal to the direction of propagation.

e.g.: let's say propagation is in the X-direction, fields will occur in Z and Y direction.
### Criteria for TEM-modes
1. Fields are contained in uniform, isotropic dielectric material
2. 2 or more conductors are required. (so rectangular waveguide doesn't support TEM), since the potential on the waveguide is the same overall in case of a single PEC.
3. The conductor must have infinite conductivity (so PEC)
4. Lossless dielectric
5. Cross-section of the tranmsision line must be constant.
### QUASI-TEM mode for MSL:
An MSL does NOT support "True" TEM mode, since the electromagnetic field exists 
- in dielectric below
- in air above
So there will be a small longitudinal component in both electric and magnetic fields (called quasi-TEM mode)


-> The higher the frequency, the higher the effect.
However at lower frequencies 

### TEM mode in stripline
In a stripline the conducting strip is placed between 2 ground planes and dielectric, which enclose the electric and magnetic fields.
So the propagation of electric and magnetic fields are entirely transverse to the direction of propagation. (No propagation in the longitudinal direction)

### Source
https://www.microwaves101.com/encyclopedias/transverse-electro-magnetic

## S-parameters
S-parameters describe the characteristics of an electric network with 2 or more ports.
They describe how much of the energy gets reflected vs passed-through to the other port when energy is applied to a first port.

### Normalization
When calculating power, using current and voltage we normalize all voltages and currents with Z0 = 50 ohms. (V = V/sqrt(Z0), I = I*sqrt(Z0)).
This number of 50 ohms is arbitrary and can be chosen as any number. It is chosen however since in RF-circuits most of the port impedances are 50 ohms, so it makes calculations easier if the goal is to match everything to 50 ohms.

### 2-port network (S-parameter calculations)
- port 1: input power a1, reflection power b1
- port 2: input power a2, reflection power b2

- S11: reflected / incoming voltage to port 1
- S21: reflected voltage at port 2 (so b2) / incoming voltage at port 1 (There is no excitation at port 1) 


$b1 = S11 * a1 + S21 * a2$

=> If no excitation applied to port 2: 
$S11 = b1 / a1$ 

$b2 = S22 * a2 + S12 * a1$

=> If no excitation applied to port 2:
$S12 = b2 / a1$



### Source
https://cds.cern.ch/record/1415639/files/p67.pdf

# Questions
## What determines the S-parameter variation?
### Context
We see that there is a S11 (reflection) parameter peak and an S21 (energy passed from port 1 to port 2) parameter drop around 3.5 GHz for the "structured.py".
- We set the load impedance to 50 ohms for port calculations

## Why is the S-parameter calculated with a reference impedance of 50 ohms, but the ports have an impedance of 0 ohms? Why not another arbitrary number?
### Context
Wee see that in "structured.py", using the CalcPort function the reference impedance of 50 ohms is passed.
- It is used to calculate the phase-shift of the voltage
- It is used to calculate the incoming current and voltage from the total incoming current and voltage.
These voltages are used further on to calculate the S-parameters.