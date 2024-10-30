

###############################################################################################
###################################### SET CONSTANTS ###########################################
###############################################################################################
### Import Libraries
import os, tempfile
from pylab import *

from CSXCAD  import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import *

### Setup the simulation
Sim_Path = os.path.join(os.getcwd(), 'Rect_WG')

post_proc_only = False
unit = 1e-6 # um

# frequency range of interest
f_0     = 24e9
lambda0 = C0/f_0/unit

#targeted mesh resolution
mesh_res = lambda0/30

###############################################################################################
###################################### INITIALIZE FDTD ########################################
###############################################################################################

### Setup FDTD parameter & excitation function
NrTS_ = 1e4
nyq_oversampling = 50
FDTD = openEMS(NrTS=NrTS_, OverSampling=nyq_oversampling)


#############################################################################################
################################# BOUNDARY CONDITIONS #######################################
#############################################################################################
# boundary conditions
# 0: PEC, 1: PMC, 2: MUR (Simple absorbing), 3:PML_8 (absorbing)
FDTD.SetBoundaryCond([0, 0, 0, 0, 3, 3])

#####################################################################################
################################# GRID / MESH #######################################
#####################################################################################

### waveguide dimensions
# WR42
a = 10700;   # waveguide width
b = 4300;    # waveguide height
length = 50000


### Setup geometry & mesh
CSX = ContinuousStructure()
FDTD.SetCSX(CSX)
mesh = CSX.GetGrid()
mesh.SetDeltaUnit(unit)

mesh.AddLine('x', [0, a])
mesh.AddLine('y', [0, b])
mesh.AddLine('z', [0, length])

####################################################################################
################################# PORTS ############################################
####################################################################################


#waveguide TE-mode definition
TE_mode = 'TE10'

## Apply the waveguide port
ports = []
start=[0, 0, 10*mesh_res]
stop =[a, b, 15*mesh_res]
mesh.AddLine('z', [start[2], stop[2]])
'''
@brief: Adding Rectangle Wave Port (MSL-port / Microstrip transmission line port)
@params:
    - port_nr: 0 (port identifier)
    - start: starting coordinates of waveguide port box
    - stop: stop coordinates of waveguide port box
    - 'z': port direction
    - a: Rectangular waveguide width
    - b: Rectangular waveguide height
    - mode_name: Type of waveguide. (TE10, TE11, TE21, ..)
    - excitation: true / false to make this port into an active feeding port or simply a passive port
- port_nr, start, stop, p_dir, a, b, mode_name, excitation
'''
ports.append(FDTD.AddRectWaveGuidePort( 0, start, stop, 'z', a*unit, b*unit, TE_mode, 1))

start=[0, 0, length-10*mesh_res]
stop =[a, b, length-15*mesh_res]
mesh.AddLine('z', [start[2], stop[2]])
ports.append(FDTD.AddRectWaveGuidePort( 1, start, stop, 'z', a*unit, b*unit, TE_mode))

mesh.SmoothMeshLines('all', mesh_res, ratio=1.4)


####################################################################################
################################# EXCITATION #######################################
####################################################################################



f_start = 20e9
f_stop  = 26e9

FDTD.SetGaussExcite(0.5*(f_start+f_stop),0.5*(f_stop-f_start))

####################################################################################
#################################### DUMPS #########################################
####################################################################################

### Define dump box...
# sub_sampling:  field domain sub-sampling -> Reducing the amount of data in domain to reduce computational cost.
Et = CSX.AddDump('Et', file_type=0, sub_sampling=[2,2,2])
start = [0, 0, 0]
stop  = [a, b, length]
Et.AddBox(start, stop)

### Run the simulation
CSX_file = os.path.join(Sim_Path, 'rect_wg.xml')
if not os.path.exists(Sim_Path):
    os.mkdir(Sim_Path)

CSX.Write2XML(CSX_file)
from CSXCAD import AppCSXCAD_BIN
os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

from CSXCAD.CSProperties import *

### FDTD SIMULATION
#! FDTD.Run(Sim_Path, cleanup=True, debug_material=True, debug_pec=True, debug_operator=True, debug_boxes=True, debug_csx=True, verbose=3)

#!############################### POST-PROCESSING #####################################
#######################################################################################
#################################### DISPLAY ##########################################
#######################################################################################
'''
*** PORTS object (CalcPort) ***
CalcPort
- freq: range of frequencies over which to calculate DFT
Reads data from file
- port_it_x / port_ut_x (current / voltage port 1) + appropriate time-step + mode purity

*** RectWGPort ***

'''

### Postprocessing & plotting
freq = linspace(f_start,f_stop,201)
for port in ports:
    port.CalcPort(Sim_Path, freq)
print(f"BETA: {ports[0].beta}")
print(f"\r\n uf_ref: {ports[0].uf_ref}\r\n")
print(f"\r\n if_ref: {ports[0].if_ref}\r\n")

### S-Parameter calculation
s11 = ports[0].uf_ref / ports[0].uf_inc
s21 = ports[1].uf_ref / ports[0].uf_inc


### Impedance calculation
ZL  = ports[0].uf_tot / ports[0].if_tot

'''
### Characteristic Impedance
DEF characteristic impedance: Characteristic transmission line impedance relates travelling voltage and current.
Function of
- Line geometry
- Material filling

### Wave impedance
DEF wave impedance: Wave impedance relates transverse field components.
Function of material constants ONLY
'''

ZL_a = ports[0].ZL # analytic waveguide impedance

## Plot s-parameter
figure()
plot(freq*1e-6,20*log10(abs(s11)),'k-',linewidth=2, label='$S_{11}$')
grid()
plot(freq*1e-6,20*log10(abs(s21)),'r--',linewidth=2, label='$S_{21}$')
legend()
ylabel('S-Parameter (dB)')
xlabel(r'frequency (MHz) $\rightarrow$')

## Compare analytic and numerical wave-impedance
figure()
plot(freq*1e-6,real(ZL), linewidth=2, label='$\Re\{Z_L\}$')
grid()
plot(freq*1e-6,imag(ZL),'r--', linewidth=2, label='$\Im\{Z_L\}$')
plot(freq*1e-6,ZL_a,'g-.',linewidth=2, label='$Z_{L, analytic}$')
ylabel('ZL $(\Omega)$')
xlabel(r'frequency (MHz) $\rightarrow$')
legend()

show()


#######################################################################################
#################################### COMMENTS #########################################
#######################################################################################


'''
Mode examples:
- TE10: has 1 lobe in the E-field strength pattern in the x-direction, 0 lobes in the y direction
- TE11: has 1 lobe in the E-field strength pattern in the x-direction and 1 lobe in the y direction
- TE21: mode has 2 lobes in the E-field pattern in the x-direction and 1 lobe in the y-direction.
Each mode has a cut-off frequnecy, because 
Frequency too low -> lobes too big -> lobe doesn't fit on the waveguide anymore.
TE10: has the lowest cutoff frequency, just as TE01 (due to symmetry, which is why we normally don't make square waveguides)

NOTE: a rectangular waveguide does not support TEM mode since there will always be a longitudinal component to the electric and/or magnetic field.
'''

'''
Excitation wave-guide port:
Are used to provide the calculation domain with power and absorb returning power.
So you basically simulate an endless rectangle / circle / whatever port you have on the other side of the waveguide.
** Exmamples **
- Circular wave-guide port
- Rectangle wave guide port
GOAL: simulate an infinitely long wave-guide connected to the port to fulfill a boundary condition.
-> https://space.mit.edu/RADIO/CST_online/mergedProjects/3D/special_overview/special_overview_waveguideover.htm

'''

'''
CalculatePort
*** READING DATA FROM FILES ***
Parameters in file
- Current: Net current coming in
- Mode purity: Refers to how well the mode that was excited propagates through the port without interference from undesired modes.
-> High mode purity: all electromagnetic energy is confined to the intended mode.

'''

'''
-> SOLVING WAVE EQUATIONS WITH DIFFERENT BOUNDARY CONDITIONS
### TEM WAVES ###
Transverse electromagnetic waves, are waves where
- Ez = Hz = 0
So all transverse fields are zero, unless kc**2 = 0; or k**2 = beta**2.
In that case
> Beta = omega * sqrt(mu * epsilon) = k
They can exist when 2 or more conductors are present.
e.g.: plane waves are TEM waves. There are no field components in the direction of propagation.
NOTE: a rectangular waveguide DOES NOT support TEM waves since the static potential in this region would be zero / constant.
Wave impedance:
> Z_TEM = Ex / Ey = omega * mu / beta = sqrt(mu / epsilon) = nu

### TE WAVES ###
Transverse electric (TE) waves are waves where
- Ez = 0
- Hz != 0
Z_TE = Ex / Hy = omega * mu / beta = k * nu / beta
NOTE: 
- Frequency dependent wave-impedance
- TE waves can be supported inside closed conductors or between more conductors

### TM WAVES ###
Transverse magnetic (TM) waves (E-Waves) are waves where
- Ez != 0
- Hz = 0
Z_TM = Ex / Hy = Beta / (omega * epsilon) = Beta * nu / k
NOTE:
- Also frequency dependent
- Also supported inside closed conductors or between conductors

-> Waveguides are conductors with metal or cylindrical cross-section.

source: https://www.microwaves101.com/encyclopedias/waveguide-wave-impedance
source: Microwave engineering, 4th edition, page 96-102
'''


'''
### Probes in waveguides for current
The probe gets an H-field function passed to it, depending on what it needs to measure.
For current measurement amperes law states that the line integral of the magnetic field over the edge of the conductor is equal to the current contained inside the intergral.
### Probes in waveguides for electric fields
The probe gets an E field function passed to it, so because the electric field within that element of the conductor surface is uniform.
The potential difference over 2 points is the line integral over the electric field from that point to the next.
'''