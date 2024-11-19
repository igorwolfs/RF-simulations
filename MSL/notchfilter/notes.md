# Simulation
## Meshing
### Meshing ratio around PEC
It is VERY IMPORTANT to always have a mesh line of:
- $2*resolution / 3$ outside of the conductor
- $resolution/3$ inside the conductor

## Probes
### Current Probe
Make sure the current probe always has
- The right area covered
- The right direction covered
- The right weight

Note that if you don't set any of these correctly, you'll get an erroneous value for your s-parameters.

> e.g.: if the weight is negative, ingoing voltage will become outgoing voltage. So if the weight of your probe at your excitation is negative, it will perceive this voltage as reflected and your reflection coefficient will suddenly go up.

## 3D geometry
### Thickness
IMPORTANT: the copper layer is positioned ON TOP of the dielectric, **NOT IN** the dielectric. 

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

**Lumped Port Measurements**
Important to note is that everything in a lumped port happens where the lumped port is positioned, so that includes
- The current measurement (in the width direction)
- The voltage measurement (in the height direction)
- The excitation (in the width/height plane)

Not sure if this is the place of excitation is an optimal location for the measurement of signals.

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
We can split the voltage signal at a port into 2 parts
- Outgoing (forward) wave V+(x), equal to a(x)
- Incoming (reflected) wave V-(x), equal to b(x)

The voltage at the port is the sum of the 2 parts:  V(x) = V+(x) + V-(x)

The current is equal to the net voltage (so the difference) divided by the feed impedance Z_0: I(x) = V+(x) / Z_ref - V-(x) / Z_0

**Feed impedance VS reference impedance**

We can assume safely however that the feed impedance is equal to the reference impedance. Even if that assumption is incorrect the S-parameter values can still be compared relative to one another.

**Calculating S-Parameters**

Now after normalizing, we can write a(x) and b(x) as a linear combination of V(x) and I(x)

- a(x) = 0.5 / sqrt(Z_ref) * (V(x) + Z_ref*I(x))
- b(x) = 0.5 / sqrt(Z_ref) * (V(x) - Z_ref*I(x))

and since:

$b1 = S11 * a1 + S21 * a2$

=> If no excitation applied to port 2: 
$S11 = b1 / a1$ 

$b2 = S22 * a2 + S12 * a1$

=> If no excitation applied to port 2:
$S12 = b2 / a1$

*note: a1 can be assumed 0 when no reflections happen back to port 1 (so impedance perfectly matched / absorption condition), a2 can be assumed 0 when no reflection happen back to port 2.*

**Power in forward / Reverse wave**
- Power in forward wave: (1/2) * a * a^
- Power in reverse wave: (1/2) * b * b^

### Source
https://cds.cern.ch/record/1415639/files/p67.pdf
https://web.ece.ucsb.edu/~long/ece145a/Notes4_Sparams.pdf

## Notchfilter

### Filtering frequency
The notch-filter will filter out frequencies with a wavelength of notch_length * 4.
This is because the wave, travelling along the notch and back, will have experienced a 180 degrees phase shift compared to the wave which just arrived at the notch. These 2 waves will subsequently cancel each other out.

The same will happen to all frequencies which have a wavelenght of 4 * notch_length / (2*n + 1), n a natural numbers.

$Z_{in} = Z_{0} * \frac{(Z_{L} + j*Z_{0} * tan(\beta * l))}{(Z_{0} + j*Z_{L} * tan(\beta * l))} $

With
- L: the length of the transmission line
- $\beta = 2 * \pi / \lambda$ 
- $Z_{L}$: the load impedance terminating the line.

In case of L being equal to $\lambda*(2*n+1)/4$
- $tan((\pi/2) * (2*n+1)) = tan(\pi /2) = infinity$

In case of a short-circuited stub the load impedance $Z_{L}$ is zero, so the total impedance becomes infinity, and the stub becomes an open circuit for those frequencies.

### Source
https://www.ittc.ku.edu/~jstiles/723/handouts/Transmission%20Line%20Input%20Impedance.pdf



## Why is the S-parameter calculated with a reference impedance of 50 ohms, but the ports have an impedance of 0 ohms? Why not another arbitrary number?
### Context
Wee see that in "structured.py", using the CalcPort function the reference impedance of 50 ohms is passed.
- It is used to calculate the phase-shift of the voltage
- It is used to calculate the incoming current and voltage from the total incoming current and voltage.
These voltages are used further on to calculate the S-parameters.

### Answer
The impedance used to calculate the current, is supposed to be the impedance of the medium.
When normalizing the voltage and currents with this impedance, it simplifies calculations of S-parameters by a lot.

One can choose a random impedance Z0 to calculate I = V / Z0, in that case the relative value of the S-parameters will still be correct (relative to the other S-parameters), however the actual values will not correspond to the real values.