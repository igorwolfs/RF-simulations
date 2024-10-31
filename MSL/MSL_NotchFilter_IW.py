# -*- coding: utf-8 -*-
"""
 Microstrip Notch Filter Tutorial

 Tested with
  - python 3.10
  - openEMS v0.0.35+

 (c) 2016-2023 Thorsten Liebig <thorsten.liebig@gmx.de>

"""

### Import Libraries
import os, tempfile
from pylab import *

from CSXCAD  import ContinuousStructure
from openEMS import openEMS

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'

### Setup the simulation
Sim_Path = os.path.join(os.getcwd(), 'NotchFilter_50')


from openEMS.physical_constants import *

###############################################################################################
###################################### INITIALIZE FDTD ########################################
###############################################################################################


### Setup FDTD parameters & excitation function
FDTD = openEMS()


#############################################################################################
################################# BOUNDARY CONDITIONS #######################################
#############################################################################################

FDTD.SetBoundaryCond( ['PML_8', 'PML_8', 'MUR', 'MUR', 'PEC', 'MUR'] )

#####################################################################################
################################# GRID / MESH #######################################
#####################################################################################
### CONSTANTS
unit = 1e-6 # specify everything in um

### MSL dimensions
MSL_length = 50000 # 5 cm
MSL_width = 600 # 0.6 mm

### Substrate dimensions
substrate_thickness = 254
substrate_epr = 3.66
stub_length = 12e3 # 12 mm

### Setup Geometry & Mesh
CSX = ContinuousStructure()
FDTD.SetCSX(CSX)
mesh = CSX.GetGrid()
mesh.SetDeltaUnit(unit)

f_max = 7e9
lambda_min = (C0/f_max) *  (1/(sqrt(substrate_epr)))
resolution = lambda_min / unit/50 # resolution of lambda/50
third_mesh = array([2*resolution/3, -resolution/3])/4

## Do manual meshing
mesh.AddLine('x', 0)
mesh.AddLine('x',  MSL_width/2+third_mesh)
mesh.AddLine('x', -MSL_width/2-third_mesh)
'''
SmoothMeshLines
Smooths the meshlines passed for that direction, with max step the resolution passed.
'''
mesh.SmoothMeshLines('x', resolution/4)

mesh.AddLine('x', [-MSL_length, MSL_length])
mesh.SmoothMeshLines('x', resolution)

mesh.AddLine('y', 0)
mesh.AddLine('y',  MSL_width/2+third_mesh)
mesh.AddLine('y', -MSL_width/2-third_mesh)
mesh.SmoothMeshLines('y', resolution/4)

mesh.AddLine('y', [-15*MSL_width, 15*MSL_width+stub_length])
mesh.AddLine('y', (MSL_width/2+stub_length)+third_mesh)
mesh.SmoothMeshLines('y', resolution)

# Create 5 points from 0 to substrate_thickness
mesh.AddLine('z', linspace(0,substrate_thickness,5))
mesh.AddLine('z', 3000)
mesh.SmoothMeshLines('z', resolution)

####################################################################################
################################# PORTS ############################################
####################################################################################

## Add the substrate + add substrate dimensions
# Default mu and ps: 1 (probably, vacuum)
substrate = CSX.AddMaterial( 'RO4350B', epsilon=substrate_epr)
subs_start = [-MSL_length, -15*MSL_width, 0]
subs_stop  = [+MSL_length, +15*MSL_width+stub_length, substrate_thickness]
substrate.AddBox(subs_start, subs_stop )

## MSL port setup
port = [None, None]
pec = CSX.AddMetal( 'PEC' )

# Excited in negative direction
'''
NOTE: 
@param: exc_dir: 'z' -> The excitation direction here is "z", which is the direction of the E-field excitation.
@param: prop_dir: 'x' -> The propagation direction, which is "x" in this case because the direction of propagation is "x".
@param: feed-shift: 10 * resolution -> Shift the port from start by a given distance in drawing units (in the propagation direction), default = 0, ONLY works when ExcitePort is set.
@param: measure plane shift: MSL_length / 3 -> Shifts the measurement plane from start a given distance (in the propagation direction) in drawing units (Default is the midldle of start / stop)
'''
portstart = [ -MSL_length, -MSL_width/2, substrate_thickness]
portstop  = [ 0,  MSL_width/2, 0]
port[0] = FDTD.AddMSLPort( 1,  pec, portstart, portstop, 'x', 'z', excite=-1, FeedShift=10*resolution, MeasPlaneShift=MSL_length/3, priority=10, Feed_R=50)

portstart = [MSL_length, -MSL_width/2, substrate_thickness]
portstop  = [0         ,  MSL_width/2, 0]
port[1] = FDTD.AddMSLPort( 2, pec, portstart, portstop, 'x', 'z', MeasPlaneShift=MSL_length/3, priority=10 , Feed_R=50)

## PEC Stub Definition in (the XY-plane)
start = [-MSL_width/2,  MSL_width/2, substrate_thickness]
stop  = [ MSL_width/2,  MSL_width/2+stub_length, substrate_thickness]
pec.AddBox(start, stop, priority=10 )


####################################################################################
################################# EXCITATION #######################################
####################################################################################

FDTD.SetGaussExcite( f_max/2, f_max/2 )

### Run the simulation
CSX_file = os.path.join(Sim_Path, 'notch.xml')

if not os.path.exists(Sim_Path):
    os.mkdir(Sim_Path)

CSX.Write2XML(CSX_file)

from CSXCAD import AppCSXCAD_BIN
os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

####################################################################################
#################################### DUMPS #########################################
####################################################################################

Et = CSX.AddDump('Et', file_type=0, sub_sampling=[2,2,2])

Et.AddBox(np.array(subs_start)*2, np.array(subs_stop)*2)

# FDTD.Run(Sim_Path, cleanup=True)
FDTD.Run(Sim_Path, cleanup=True, debug_material=True, debug_pec=True, debug_operator=True, debug_boxes=True, debug_csx=True, verbose=3)


#!############################### POST-PROCESSING #####################################
#######################################################################################
#################################### DISPLAY ##########################################
#######################################################################################

### Post-processing and plotting
f = linspace( 1e6, f_max, 1601 )
for p in port:
    '''
    QUESTION: how can there be a reference impedance here when there is no feed impedance specified at the MSL-ports?
    '''
    p.CalcPort( Sim_Path, f, ref_impedance = 50)

s11 = port[0].uf_ref / port[0].uf_inc
s21 = port[1].uf_ref / port[0].uf_inc

plot(f/1e9,20*log10(abs(s11)),'k-',linewidth=2 , label='$S_{11}$')
grid()
plot(f/1e9,20*log10(abs(s21)),'r--',linewidth=2 , label='$S_{21}$')
legend()
ylabel('S-Parameter (dB)')
xlabel('frequency (GHz)')
ylim([-40, 2])

show()


#######################################################################################
#################################### COMMENTS #########################################
#######################################################################################

'''
#! QUASI-TEM mode for MSL: 
An MSL does NOT support "True" TEM mode, since the electromagnetic field exists 
- in dielectric below
- in air above
So there will be a small longitudinal component in both electric and magnetic fields (called quasi-TEM mode)
-> The higher the frequency, the higher the effect.
However at lower frequencies 
#! TEM mode in stripline
In a stripline the conducting strip is placed between 2 ground planes and dielectric, which enclose the electric and magnetic fields.
So the propagation of electric and magnetic fields are entirely transverse to the direction of propagation. (No propagation in the longitudinal direction)
'''

'''
NOTE: WHEN VISUALIZING THE ELECTRIC FIELD
-> Make sure to rightly scale the electric field, so everything doesn't simply turn red whenever a minor electric field passes through.
'''

'''
QUESTION:
What is the difference between an "excited"-port and a "non-excited" port?
- An excited port has an excitation defined in the csxcad file.
HOWEVER: the relevant mode-function is added to all relevant probes (in this case an I and U-probe)
- i_probe = CSX.AddProbe(self.I_filenames[0], p_type=11, weight=self.direction, mode_function=self.H_func)
- u_probe = CSX.AddProbe(self.U_filenames[0], p_type=10, mode_function=self.E_func)
The main question then becomes, why does a probe need a mode function?
ANSWER: 
'''

'''
QUESTION:
- Difference between the situation with and without 50 ohm impedance port instead of an infinite impedance port which just absorbs everything (my guess is the BC is absorbing)
ANSWER: 

'''

'''
QUESTION:
- How do we calculate the s-parameter values from the in and output voltage and currents? 
ANSWER: 

'''

