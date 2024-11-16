'''
Basic example taken from theliebig
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
unit = 1e-3 # specify everything in mm

## prepare simulation folder
currDir = os.getcwd()
file_name = 'structured'
Plot_Path = os.path.join(currDir, file_name)
Sim_Path = os.path.join(Plot_Path, file_name)
Sim_CSX = 'MSL_copper.xml'
if not (os.path.exists(Plot_Path)):
	os.mkdir(Plot_Path)
	os.mkdir(Sim_Path)
else:
	shutil.rmtree(Sim_Path)
	os.mkdir(Sim_Path)


## setup FDTD parameter & excitation function
CSX = ContinuousStructure()
max_timesteps = 2000
min_decrement = 1e-5 # equivalent to -50 dB
FDTD = openEMS(NrTS=max_timesteps,EndCriteria=min_decrement)
FDTD.SetCSX(CSX)
#######################################################################################################################################
# BOUNDARY CONDITIONS
#######################################################################################################################################

# Propagation direction: x-dir
FDTD.SetBoundaryCond( ['MUR', 'MUR', 'PMC', 'PMC', 'PEC', 'PMC'] )
# FDTD.SetBoundaryCond( ['PML_8', 'PML_8', 'MUR', 'MUR', 'PEC', 'MUR'] )

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


## MATERIAL - AIR
materialList['air'] = CSX.AddMaterial( 'air' )
air_dx = 600
air_dy = 400
air_dz = 200

## MATERIAL - PEC
materialList['copper'] = CSX.AddMaterial( 'copper' )
materialList['copper'].SetMaterialProperty(epsilon=1.0, mue=1.0, kappa=56e6)
MSL_dx = 600 # 600 mm
MSL_dy = 50 # 50 mm
MSL_dz = 10  # 10 mm


## MATERIAL - fakepml
# this "pml" is a normal material with graded losses
# electric and magnetic losses are related to give low reflection
# for normally incident TEM waves
abs_length = 100 # Absorber length
substrate_epr = 3.66
substrate_thickness = 254
finalKappa = 1/abs_length**2
finalSigma = finalKappa*MUE0/EPS0
materialList['fakepml'] = CSX.AddMaterial( 'fakepml', kappa=finalKappa, sigma=finalSigma)
materialList['fakepml'].SetMaterialProperty(epsilon=1.0, mue=1.0, kappa=56e6)
materialList['fakepml'].SetMaterialWeight(kappa='pow(x-' + str(MSL_dx-abs_length) + ',2)',  sigma='pow(x-' + str(MSL_dx-abs_length) + ',2)')

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
wavelength_min = C0/(f0+fc)
wavelength_min_u = wavelength_min / unit

## Setup Geometry & Mesh
resolution_u = wavelength_min_u / 15 # resolution of lambda/50

from CSXCAD.SmoothMeshLines import SmoothMeshLines

mesh.x = np.concatenate((mesh.x, np.array([0, air_dx])))
mesh.x = SmoothMeshLines(mesh.x, resolution_u)

mesh.y = np.concatenate((mesh.y, np.array([-air_dy/2, air_dy/2, -MSL_dy/2, MSL_dy/2])))
mesh.y = SmoothMeshLines(mesh.y, resolution_u)

mesh.z = np.concatenate((mesh.z, linspace(0, MSL_dz, 5), np.array([MSL_dz+1, air_dz])))
mesh.z = SmoothMeshLines(mesh.z, resolution_u)

#### * BOXES

## Excitation
## Add excitation below the strip
exc_start = [mesh.x[0], -MSL_dy/2 , 0]
exc_stop  = [mesh.x[0],  MSL_dy/2 , MSL_dz]

excitation = CSX.AddExcitation('excite', exc_type=0, exc_val=[0, 0, -1], delay=0)
excitation.AddBox(exc_start, exc_stop) # priority = 

## COPPER

copper_start = [0, 	-MSL_dy/2,   MSL_dz]
copper_stop  = [MSL_dx, MSL_dy/2, 	MSL_dz+1]
copper_priority = 100 # the geometric priority is set to 100
materialList['copper'].AddBox( copper_start, copper_stop, priority=copper_priority)


## fake pml
pml_start = [MSL_dx - abs_length, mesh.y[0] , mesh.z[0]]
pml_stop  = [MSL_dx				, mesh.y[-1], mesh.z[-1]]
pml_priority = 0
materialList['fakepml'].AddBox(pml_start, pml_stop, priority=pml_priority)


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
et_start = [mesh.x[0], mesh.y[0], MSL_dz]
et_stop  = [mesh.x[-1], mesh.y[-1], MSL_dz]
dump_boxes['et'] = CSX.AddDump( 'Et_', dump_mode=2 ) # cell interpolated
dump_boxes['et'].AddBox(et_start, et_stop, priority=0 )
dump_boxes['ht'] = CSX.AddDump(  'Ht_', dump_type=1, dump_mode=2 ) # cell interpolated
dump_boxes['ht'].AddBox(et_start, et_stop, priority=0 )

## define voltage calc box
# voltage calc boxes will automatically snap to the next mesh-line
# z -> x
# x -> y
# y -> z

dump_boxes['ut1'] = CSX.AddProbe(  'ut1', 0 )
interpl_x  = interp1d( mesh.x, np.arange(0,mesh.x.size, 1), kind='nearest', fill_value="extrapolate")
xidx_ut1 = int(interpl_x(MSL_dx/2)) # length / 2

print(f"mesh.z: {mesh.z}, x_idx: {xidx_ut1}, len: {len(mesh.z)}")
ut1_start = [mesh.x[xidx_ut1], 0, MSL_dz]
ut1_stop  = [mesh.x[xidx_ut1], 0, 0]
dump_boxes['ut1'].AddBox(ut1_start, ut1_stop, priority=0)

# add a second voltage probe to compensate space offset between voltage and
# current

dump_boxes['ut2'] = CSX.AddProbe(  'ut2', 0 )
ut2_start = [mesh.x[xidx_ut1+1], 0, MSL_dz]
ut2_stop  = [mesh.x[xidx_ut1+1], 0, 0]
dump_boxes['ut2'].AddBox(ut2_start, ut2_stop, priority=0)


## define current calc box
# current calc boxes will automatically snap to the next dual mesh-line
dump_boxes['it1'] = CSX.AddProbe( 'it1', 1 )

'''
interp1d: returns a function that interpolates between the values x, y passed
'''
interpl_y1  = interp1d( mesh.y, np.arange(0,mesh.y.size, 1), kind='nearest', fill_value="extrapolate")
yidx1 = int(interpl_x(-MSL_dy/2)) # width / 2
interpl_y2  = interp1d( mesh.y, np.arange(0,mesh.y.size, 1), kind='nearest', fill_value="extrapolate")
yidx2 = int(interpl_x(MSL_dy/2)) # width / 2

ydelta = diff(mesh.y)

interpl_z1  = interp1d( mesh.z, np.arange(0,mesh.z.size, 1), kind='nearest', fill_value="extrapolate")
zidx1 = int(interpl_z1(MSL_dz)) # height
interpl_z2  = interp1d( mesh.z, np.arange(0,mesh.z.size, 1), kind='nearest', fill_value="extrapolate")
zidx2 = int(interpl_z2(MSL_dz+1)) # height+1

zdelta = diff(mesh.z)
xdelta = diff(mesh.x)

start_it1 = [mesh.x[xidx_ut1]+xdelta[xidx_ut1]/2, mesh.y[yidx1]-ydelta[yidx1-1]/2, mesh.z[zidx1]-zdelta[zidx1-1]/2]
stop_it1 = [mesh.x[xidx_ut1]+xdelta[xidx_ut1]/2,  mesh.y[yidx2]+xdelta[yidx2]/2,   mesh.z[zidx2]+zdelta[zidx2]/2]
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
figure()

ut1_t, ut1_V = U.ui_time[0], U.ui_val[0] # ut1 time voltage 
et_t, et_V = U.ui_time[3], U.ui_val[3] # et time electric field

# Plotting
plot(ut1_t, ut1_V, 'k-',linewidth=2 , label='$ut1$')
grid()
plot(et_t, et_V,'r--',linewidth=2 , label='$et$')
legend()
ylabel('time domain voltage')
xlabel('time (t / ns)')
y1_max, y1_min = max(ut1_V), min(ut1_V)
y2_max, y2_min = max(et_V), min(et_V)
ylim([min(y1_min, y2_min), max(y1_max, y2_max)])

plt.savefig(os.path.join(Plot_Path, 'voltages.pdf'))
show()

## Characteristic impedance calculation
U = (U.ui_f_val[0] + U.ui_f_val[1]) / 2
Z = U / I.ui_f_val[0]


figure()
plot(f*1e-6, real(Z), linewidth=2, label='$\Re\{Z\}$')
grid()
plot(f*1e-6, imag(Z),'r--', linewidth=2, label='$\Im\{Z\}$')
xlabel(r'frequency (MHz) $\rightarrow$')
ylabel('ZL $(\Omega)$')
legend('real', 'imag')

plt.savefig(os.path.join(Plot_Path, 'impedance.pdf'))

show()