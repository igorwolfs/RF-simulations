'''
# * GOAL:
The goal here is to simply to 
- represent a 50 ohm MSL
- plot its S-parameters (which should have a 0 reflection coefficient)
- plot its voltages
'''



### Import Libraries
import os, tempfile
from pylab import *
import shutil
from CSXCAD  import ContinuousStructure
from openEMS import openEMS

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'


### CONSTANTS
from openEMS.physical_constants import *
unit = 1e-6 # specify everything in mm


## SIMULATION FOLDER SETUP
currDir = os.getcwd()
file_name = os.path.basename(__file__).strip('.py')
Plot_Path = os.path.join(currDir, file_name)
Sim_Path = os.path.join(Plot_Path, file_name)
if not (os.path.exists(Plot_Path)):
	os.mkdir(Plot_Path)
	os.mkdir(Sim_Path)
else:
	shutil.rmtree(Sim_Path)
	os.mkdir(Sim_Path)


## setup FDTD parameter & excitation function
CSX = ContinuousStructure()
max_timesteps = 200000
min_decrement = 1e-5 # equivalent to -50 dB
FDTD = openEMS(NrTS=1000000000)#NrTS=max_timesteps,EndCriteria=min_decrement)
FDTD.SetCSX(CSX)
#######################################################################################################################################
# BOUNDARY CONDITIONS
#######################################################################################################################################

'''
EFFECT OF DIFFERENT BOUNDARY CONDITIONS:
# * FDTD.SetBoundaryCond( ['PML_8', 'PML_8', 'PMC', 'PMC', 'PEC', 'PMC'] )
Shows weird reflections

# * FDTD.SetBoundaryCond( ['MUR', 'MUR', 'PMC', 'PMC', 'PEC', 'PMC'] )
Brings us close to the expected result.

# * FDTD.SetBoundaryCond( ['MUR', 'MUR', 'MUR', 'MUR', 'PEC', 'MUR'] )
Brings us close to the expected result.

# * CONCLUSION
=> It seems like the PML_8 boundary is really to blame for some of the weird reflections. We have to really be carefull about how and when to use the PML_8 boundary.
=> The difference between adding the MUR boundary instead of the PMC is minor, there is some difference in reflection but it's not that noticeable.
'''

# Propagation direction: x-dir
FDTD.SetBoundaryCond( ['MUR', 'MUR', 'MUR', 'MUR', 'PEC', 'MUR'] )

#######################################################################################################################################
# COORDINATE SYSTEM
#######################################################################################################################################
def mesh():
	x,y,z
      
openEMS_grid = CSX.GetGrid()
openEMS_grid.SetDeltaUnit(unit)

mesh.x = np.array([])
mesh.y = np.array([])
mesh.z = np.array([])



#######################################################################################################################################
# MATERIALS
#######################################################################################################################################

materialList = {}


## MATERIAL - PEC
materialList['copper'] = CSX.AddMaterial( 'copper' )
materialList['copper'].SetMaterialProperty(epsilon=1.0, mue=1.0, kappa=56e6)
MSL_dx = 200e3 # 50 mm
MSL_dy = 360   # 0.361 mm
MSL_dz = 35    # 0.035 mm
copper_priority = 20

## MATERIAL - AIR
materialList['air'] = CSX.AddMaterial( 'air' )
air_dx = MSL_dx
air_dy = 500*MSL_dy
air_dz = 5e3 # > 20 times the substrate height
air_priority = 0


## MATERIAL - FR4
substrate_eps = 3.8
materialList['FR4'] = CSX.AddMaterial( 'FR4', epsilon=substrate_eps)
substrate_dx = MSL_dx
substrate_dy = air_dy
substrate_dz = 206    # Impedance matched 206 zm
substrate_priority = 1

#######################################################################################################################################
# EXCITATION Gaussian
#######################################################################################################################################

f0 = 2e9 # center frequency
fc = 1e9 # 10 dB corner frequency (in this case 1e9 Hz - 3e9 Hz)

FDTD.SetGaussExcite( f0, fc)

#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################

## WAVELENGTH
wavelength_min = C0/(f0+fc) / sqrt(substrate_eps)
wavelength_min_u = wavelength_min / unit

## eometry & Mesh Setup
resolution_u = wavelength_min_u / 15 # resolution of lambda/50

from CSXCAD.SmoothMeshLines import SmoothMeshLines


mesh.x = np.concatenate((mesh.x, np.array([0, air_dx])))
mesh.x = SmoothMeshLines(mesh.x, resolution_u)
print(f"Resolution_u: {resolution_u}")


mesh.y = np.concatenate((mesh.y, np.array([-air_dy/2, air_dy/2, -MSL_dy/2, MSL_dy/2])))
mesh_third_dy = np.array([-MSL_dy/3, MSL_dy*2/3])
mesh.y = np.concatenate((mesh.y, mesh_third_dy+MSL_dy/2, -mesh_third_dy-MSL_dy/2))
mesh.y = SmoothMeshLines(mesh.y, resolution_u)


mesh.z = np.concatenate((mesh.z, linspace(0, substrate_dz, 5), np.array([substrate_dz+MSL_dz, air_dz])))
mesh_third_dz = np.array([-MSL_dz/3, MSL_dz*2/3]) / 4
mesh.z = np.concatenate((mesh.z, (substrate_dz+MSL_dz/2) + mesh_third_dz, (substrate_dz - MSL_dz/2) - mesh_third_dz))
mesh.z = SmoothMeshLines(mesh.z, resolution_u)


#### * BOXES
## Excitation
## Add excitation below the strip
exc_start = [mesh.x[5], -MSL_dy/2 , 0]
exc_stop  = [mesh.x[5],  MSL_dy/2 , substrate_dz]

excitation = CSX.AddExcitation('excite', exc_type=0, exc_val=[0, 0, -1], delay=0)
excitation.AddBox(exc_start, exc_stop)

## COPPER
copper_start = [0, 	   -MSL_dy/2,   substrate_dz]
copper_stop  = [MSL_dx, MSL_dy/2, 	substrate_dz+MSL_dz]
materialList['copper'].AddBox( copper_start, copper_stop, priority=copper_priority)

## FR4
substrate_start = [0, 			 mesh.y[0] , 0]
substrate_stop  = [substrate_dx, mesh.y[-1], substrate_dz]
materialList['FR4'].AddBox(substrate_start, substrate_stop, priority=substrate_priority)


## Add lines to grid
openEMS_grid.AddLine('x', mesh.x)
openEMS_grid.AddLine('y', mesh.y)
openEMS_grid.AddLine('z', mesh.z)

#######################################################################################################################################
# PROBES
#######################################################################################################################################
from scipy.interpolate import interp1d

dump_boxes = {}
## define dump boxes
et_start = [mesh.x[0], mesh.y[0], substrate_dz]
et_stop  = [mesh.x[-1], mesh.y[-1], substrate_dz]
dump_boxes['et'] = CSX.AddDump( 'Et_', dump_mode=2 ) # cell interpolated
dump_boxes['et'].AddBox(et_start, et_stop, priority=0 )
dump_boxes['ht'] = CSX.AddDump(  'Ht_', dump_type=1, dump_mode=2 ) # cell interpolated
dump_boxes['ht'].AddBox(et_start, et_stop, priority=0 )

## define voltage calc box
dump_boxes['ut1'] = CSX.AddProbe(  'ut1', 0 )
interpl_x  = interp1d( mesh.x, np.arange(0,mesh.x.size, 1), kind='nearest', fill_value="extrapolate")
xidx_ut1 = int(interpl_x(MSL_dx/2)) # length / 2

ut1_start = [mesh.x[xidx_ut1], 0, substrate_dz]
ut1_stop  = [mesh.x[xidx_ut1], 0, 0]
print(f"\r\nut1: {ut1_start} -> {ut1_stop}")
dump_boxes['ut1'].AddBox(ut1_start, ut1_stop, priority=0)

# add a second voltage probe to compensate space offset between voltage and current
dump_boxes['ut2'] = CSX.AddProbe(  'ut2', 0 )
ut2_start = [mesh.x[xidx_ut1+1], 0, substrate_dz]
ut2_stop  = [mesh.x[xidx_ut1+1], 0, 0]
print(f"ut2: {ut2_start} -> {ut2_stop}")
dump_boxes['ut2'].AddBox(ut2_start, ut2_stop, priority=0)


## define current calc box
# current calc boxes will automatically snap to the next dual mesh-line
dump_boxes['it1'] = CSX.AddProbe( 'it1', 1 )

'''
interp1d: returns a function that interpolates between the values x, y passed
'''
interpl_y1  = interp1d( mesh.y, np.arange(0,mesh.y.size, 1), kind='nearest', fill_value="extrapolate")
yidx1 = int(interpl_y1(-MSL_dy/2)) # width / 2
interpl_y2  = interp1d( mesh.y, np.arange(0,mesh.y.size, 1), kind='nearest', fill_value="extrapolate")
yidx2 = int(interpl_y2(MSL_dy/2)) # width / 2

ydelta = diff(mesh.y)

interpl_z1  = interp1d( mesh.z, np.arange(0,mesh.z.size, 1), kind='nearest', fill_value="extrapolate")
zidx1 = int(interpl_z1(substrate_dz)) # height
interpl_z2  = interp1d( mesh.z, np.arange(0,mesh.z.size, 1), kind='nearest', fill_value="extrapolate")
zidx2 = int(interpl_z2(substrate_dz+MSL_dz)) # height+1

zdelta = diff(mesh.z)
xdelta = diff(mesh.x)

start_it1 = [mesh.x[xidx_ut1]+xdelta[xidx_ut1]/2, mesh.y[yidx1]-ydelta[yidx1-1]/2, mesh.z[zidx1]-zdelta[zidx1-1]/2]
stop_it1 = [mesh.x[xidx_ut1]+xdelta[xidx_ut1]/2,  mesh.y[yidx2]+ydelta[yidx2]/2,   mesh.z[zidx2]+zdelta[zidx2]/2]
print(f"it1: {start_it1} -> {stop_it1}")

dump_boxes['it1'].AddBox(start_it1, stop_it1, priority=0)

#######################################################################################################################################
# RUN
#######################################################################################################################################

### Run the simulation
CSX_file = os.path.join(Sim_Path, 'notch.xml')
if not os.path.exists(Sim_Path):
    os.mkdir(Sim_Path)
CSX.Write2XML(CSX_file)
from CSXCAD import AppCSXCAD_BIN
os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

# FDTD.Run(Sim_Path, cleanup=True)
FDTD.Run(Sim_Path, cleanup=True, debug_material=True, debug_pec=True, debug_operator=True, debug_boxes=True, debug_csx=True, verbose=3)


#######################################################################################################################################
# POST_PROCESSING
#######################################################################################################################################
### Run the simulation

from openEMS.ports import UI_data
freq = linspace( f0-fc, f0+fc, 501)

U = UI_data(['ut1', 'ut2', 'et'], Sim_Path, freq) # Time domain/freq domain voltage
I = UI_data(['it1'], Sim_Path, freq) # time domain / freq domain current (half time step offset is corrected? in octave?)

## Plot time domain voltage



ut1_t, ut1_V = U.ui_time[0], U.ui_val[0] # ut1 time voltage 
et_t, et_V = U.ui_time[2], U.ui_val[2] # et time electric field

# Plotting
# * figure()
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(ut1_t, ut1_V, 'g-', linewidth=2, label='$ut1$')
ax2.plot(et_t, et_V, 'b-', linewidth=2, label='$et$')

ax1.set_xlabel('time (t / ns)')
ax1.set_ylabel('Volts (V)', color='g')
ax2.set_ylabel('E-field (V/m)', color='b')

plt.savefig(os.path.join(Plot_Path, 'voltages.pdf'))
plt.show()


## Characteristic impedance calculation
U = (U.ui_f_val[0] + U.ui_f_val[1]) / 2
Z = U / I.ui_f_val[0]


fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(freq*1e-6, real(Z), 'g-', linewidth=2, label='$\Re\{Z\}$')
ax1.plot(freq*1e-6, imag(Z), 'b-', linewidth=2, label='$\Im\{Z\}$')
ax1.set_xlabel('frequency [Hz]')
ax1.set_ylabel('Re [Ohm]', color='g')
ax2.set_ylabel('Im [Ohm]', color='b')
ax2.set_ylim(ax1.get_ylim())
plt.savefig(os.path.join(Plot_Path, 'impedance.pdf'))
plt.show()