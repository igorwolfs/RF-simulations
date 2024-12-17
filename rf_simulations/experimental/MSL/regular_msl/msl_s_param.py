'''
Basic example taken from theliebig, removed the PML
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
max_timesteps = 1600
min_decrement = 1e-5 # equivalent to -50 dB

#! WARNING: When NOT using these max_timesteps, the MSL keeps reflecting back and forth until the energy number reaches infinity
FDTD = openEMS(NrTS=max_timesteps,EndCriteria=min_decrement)
FDTD.SetCSX(CSX)
#######################################################################################################################################
# BOUNDARY CONDITIONS
#######################################################################################################################################

# Propagation direction: x-dir
FDTD.SetBoundaryCond( ['PML_8', 'MUR', 'PMC', 'PMC', 'PEC', 'PMC'] )
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
MSL_dz = 1  # 10 mm
substrate_dz = 10 # 10 mm

## MATERIAL - fakepml
fakepml_dx = 100 # Absorber length
fakepml_epr = 3.66
fakepml_thickness = 254
fakepml_finalKappa = 1/fakepml_dx**2
fakepml_finalSigma = fakepml_finalKappa*MUE0/EPS0
materialList['fakepml'] = CSX.AddMaterial( 'fakepml', kappa=fakepml_finalKappa, sigma=fakepml_finalSigma)
materialList['fakepml'].SetMaterialWeight(kappa='pow(x-' + str(MSL_dx-fakepml_dx) + ',2)', sigma='pow(x-' + str(MSL_dx-fakepml_dx) + ',2)')

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

mesh.z = np.concatenate((mesh.z, linspace(0, substrate_dz, 5), np.array([substrate_dz+MSL_dz, air_dz])))
mesh.z = SmoothMeshLines(mesh.z, resolution_u)

#### * BOXES
## Excitation
## Add excitation below the strip
exc_start = [mesh.x[9], -MSL_dy/2 , substrate_dz]
exc_stop  = [mesh.x[9],  MSL_dy/2 , 0]
exc_priority=10
excitation = CSX.AddExcitation('excite', exc_type=0, exc_val=[0, 0, -1], delay=0)
excitation.AddBox(exc_start, exc_stop, priority = exc_priority) 

## COPPER

copper_start = [0, 	-MSL_dy/2,   substrate_dz]
copper_stop  = [MSL_dx, MSL_dy/2, 	substrate_dz+MSL_dz]
copper_priority = 100 # the geometric priority is set to 100
materialList['copper'].AddBox( copper_start, copper_stop, priority=copper_priority)


## fake pml
pml_start = [MSL_dx - fakepml_dx, mesh.y[0] , mesh.z[0]]
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
et_start = [mesh.x[0], mesh.y[0], substrate_dz]
et_stop  = [mesh.x[-1], mesh.y[-1], substrate_dz]
dump_boxes['et'] = CSX.AddDump( 'Et_', dump_mode=2 ) # cell interpolated
dump_boxes['et'].AddBox(et_start, et_stop, priority=0 )
dump_boxes['ht'] = CSX.AddDump(  'Ht_', dump_type=1, dump_mode=2 ) # cell interpolated
dump_boxes['ht'].AddBox(et_start, et_stop, priority=0 )

### Grid functions for interpolation

'''
interp1d: returns a function that interpolates between the values x, y passed
'''
interpl_x  = interp1d( mesh.x, np.arange(0,mesh.x.size, 1), kind='nearest', fill_value="extrapolate")
interpl_y  = interp1d( mesh.y, np.arange(0,mesh.y.size, 1), kind='nearest', fill_value="extrapolate")
interpl_z = interp1d( mesh.z, np.arange(0,mesh.z.size, 1), kind='nearest', fill_value="extrapolate")

xdelta = diff(mesh.x)
ydelta = diff(mesh.y)
zdelta = diff(mesh.z)


##! * INPUT PORT COORDS
in_xidx = int(interpl_x(MSL_dx/6)) # length / 2
in_yidx1 = int(interpl_y(-MSL_dy/2)) # width / 2
in_yidx2 = int(interpl_y(MSL_dy/2)) # width / 2
in_zidx1 = int(interpl_z(substrate_dz)) # height
in_zidx2 = int(interpl_z(substrate_dz+MSL_dz)) # height+1


###### define voltage calc box
##! * INPUT PORT
# * INPUT PORT LOWER
# port_weight = 0.5
port_weight = 1

dump_boxes['in_ut1_A'] = CSX.AddProbe(  'in_ut1_A', 0, weight=port_weight )
in_ut1_A_start = [mesh.x[in_xidx], 0, substrate_dz]
in_ut1_A_stop  = [mesh.x[in_xidx], 0, 0]
dump_boxes['in_ut1_A'].AddBox(in_ut1_A_start, in_ut1_A_stop, priority=0)

# add a second voltage probe to compensate space offset between voltage and current
dump_boxes['in_ut1_B'] = CSX.AddProbe(  'in_ut1_B', 0, weight=port_weight )
in_ut1_B_start = [mesh.x[in_xidx+1], 0, substrate_dz]
in_ut1_B_stop  = [mesh.x[in_xidx+1], 0, 0]
dump_boxes['in_ut1_B'].AddBox(in_ut1_B_start, in_ut1_B_stop, priority=0)

# * INPUT PORT LOWER
'''
dump_boxes['in_ut2_A'] = CSX.AddProbe(  'in_ut2_A', 0, weight=port_weight )
in_ut2_A_start = [mesh.x[in_xidx], 0, substrate_dz]
in_ut2_A_stop  = [mesh.x[in_xidx], 0, air_dz]
dump_boxes['in_ut2_A'].AddBox(in_ut2_A_start, in_ut2_A_stop, priority=0)

# # * Add a second voltage probe to compensate space offset between voltage and current
dump_boxes['in_ut2_B'] = CSX.AddProbe(  'in_ut2_B', 0, weight=port_weight )
in_ut2_B_start = [mesh.x[in_xidx+1], 0, substrate_dz]
in_ut2_B_stop  = [mesh.x[in_xidx+1], 0, air_dz]
dump_boxes['in_ut2_B'].AddBox(in_ut2_B_start, in_ut2_B_stop, priority=0)
'''

# * CURRENT PORT
dump_boxes['in_it_A'] = CSX.AddProbe( 'in_it_A', p_type=1, weight=1, norm_dir=0 )
in_start_it_A = [mesh.x[in_xidx]+xdelta[in_xidx]/2, mesh.y[in_yidx1]-ydelta[in_yidx1-1]/2, mesh.z[in_zidx1]-zdelta[in_zidx1-1]/2]
in_stop_it_A = [mesh.x[in_xidx]+xdelta[in_xidx]/2,  mesh.y[in_yidx2]+ydelta[in_yidx2]/2,   mesh.z[in_zidx2]+zdelta[in_zidx2+1]/2]
dump_boxes['in_it_A'].AddBox(in_start_it_A, in_stop_it_A, priority=0)

#! OUTPUT PORT UPPER
out_xidx  = int(interpl_x(MSL_dx - MSL_dx/4)) #int(interpl_x(SL_dx*3/4))   # length / 4
out_yidx1 = int(interpl_y(-MSL_dy/2))    # width / 2
out_yidx2 = int(interpl_y(MSL_dy/2))     # width / 2
out_zidx1 = int(interpl_z(substrate_dz)) # height
out_zidx2 = int(interpl_z(substrate_dz+MSL_dz)) # height+1


# * PORT OUT
dump_boxes['out_ut1_A'] = CSX.AddProbe(  'out_ut1_A', 0, weight=port_weight )
out_ut1_A_start = [mesh.x[out_xidx], 0, substrate_dz]
out_ut1_A_stop  = [mesh.x[out_xidx], 0, 0]
dump_boxes['out_ut1_A'].AddBox(out_ut1_A_start, out_ut1_A_stop, priority=0)

# add a second voltage probe to compensate space offset between voltage and current

dump_boxes['out_ut1_B'] = CSX.AddProbe(  'out_ut1_B', 0, weight=port_weight )
out_ut1_B_start = [mesh.x[out_xidx+1], 0, substrate_dz]
out_ut1_B_stop  = [mesh.x[out_xidx+1], 0, 0]
dump_boxes['out_ut1_B'].AddBox(out_ut1_B_start, out_ut1_B_stop, priority=0)

#! INPUT PORT LOWER
'''
dump_boxes['out_ut2_A'] = CSX.AddProbe(  'out_ut2_A', 0, weight=port_weight )
out_ut2_A_start = [mesh.x[out_xidx], 0, substrate_dz]
out_ut2_A_stop  = [mesh.x[out_xidx], 0, air_dz]
dump_boxes['out_ut2_A'].AddBox(out_ut2_A_start, out_ut2_A_stop, priority=0)

# # add a second voltage probe to compensate space offset between voltage and current

dump_boxes['out_ut2_B'] = CSX.AddProbe(  'out_ut2_B', 0, weight=port_weight )
out_ut2_B_start = [mesh.x[out_xidx+1], 0, substrate_dz]
out_ut2_B_stop  = [mesh.x[out_xidx+1], 0, air_dz]
dump_boxes['out_ut2_B'].AddBox(out_ut2_B_start, out_ut2_B_stop, priority=0)

'''

## define current calc box
# current calc boxes will automatically snap to the next dual mesh-line
dump_boxes['out_it_A'] = CSX.AddProbe( 'out_it_A', p_type=1, weight=-1, norm_dir=0 )
out_start_it_A = [mesh.x[out_xidx]+xdelta[out_xidx]/2, mesh.y[out_yidx1]-ydelta[out_yidx1-1]/2, mesh.z[out_zidx1]-zdelta[out_zidx1-1]/2]
out_stop_it_A = [mesh.x[out_xidx]+xdelta[out_xidx]/2,  mesh.y[out_yidx2]+ydelta[out_yidx2]/2,   mesh.z[out_zidx2]+zdelta[out_zidx2+1]/2]
dump_boxes['out_it_A'].AddBox(out_start_it_A, out_stop_it_A, priority=0)


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
freq = linspace( f0-fc, f0+fc, 1601)

E_field = UI_data(['et'], Sim_Path, freq)
U1_in = UI_data(['in_ut1_A', 'in_ut1_B'], Sim_Path, freq) # Time domain/freq domain voltage
#U2_in = UI_data(['in_ut2_A', 'in_ut2_B'], Sim_Path, freq) # Time domain/freq domain voltage

U1_out = UI_data(['out_ut1_A', 'out_ut1_B'], Sim_Path, freq) # Time domain/freq domain voltage
#U2_out = UI_data(['out_ut2_A', 'out_ut2_B'], Sim_Path, freq) # Time domain/freq domain voltage
I_in = UI_data(['in_it_A'], Sim_Path, freq) # time domain / freq domain current (half time step offset is corrected? in octave?)
I_out = UI_data(['out_it_A'], Sim_Path, freq) # time domain / freq domain current (half time step offset is corrected? in octave?)


### current, voltage lists
in_i_f = []
in_u_f = []
in_u_t = []
out_u_f = []
out_u_t = []
out_i_f = []

for i in range(2):
	if (i < 1):
		in_i_f.append(I_in.ui_f_val[i])
		out_i_f.append(I_out.ui_f_val[i])
	in_u_f.append(U1_in.ui_f_val[i]) # + U2_in.ui_f_val[i])
	in_u_t.append(U1_in.ui_val[i]) # + U2_in.ui_val[i])
	out_u_f.append(U1_out.ui_f_val[i]) # + U2_out.ui_f_val[i])
	out_u_t.append(U1_out.ui_val[i]) # + U2_out.ui_val[i])

### Plot time domain voltage
uf_in_tot = (in_u_f[0] + in_u_f[1]) / 2
ut_in_tot = (in_u_t[0] + in_u_t[1]) / 2
u_t_array = U1_in.ui_time[0]
if_in_tot = in_i_f[0]
uf_out_tot = (out_u_f[0] + out_u_f[1]) / 2
ut_out_tot = (out_u_t[0] + out_u_t[1]) / 2
if_out_tot = out_i_f[0]

et_t_array, et_V = E_field.ui_time[0], E_field.ui_val[0] # et time electric field

### Plotting
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(u_t_array, ut_in_tot, 'g-', linewidth=2, label='$ut1$')
ax2.plot(et_t_array, et_V, 'b-', linewidth=2, label='$et$')

ax1.set_xlabel('time (t / ns)')
ax1.set_ylabel('Volts (V)', color='g')
ax2.set_ylabel('E-field (V/m)', color='b')

plt.savefig(os.path.join(Plot_Path, 'voltages.pdf'))
plt.show()


## Characteristic impedance calculation
Z = uf_in_tot / if_in_tot
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


## S-Parameters
# MSL Length: 100 mm
# eps: 3.66
Z_ref = 50.0


## Excitation applied at port 1 only:
a1 = 1/(2*sqrt(Z_ref)) * (uf_in_tot + Z_ref * if_in_tot)
b1 = 1/(2*sqrt(Z_ref)) * (uf_in_tot - Z_ref * if_in_tot)
a2 = 1/(2*sqrt(Z_ref)) * (uf_out_tot + Z_ref * if_out_tot)
b2 = 1/(2*sqrt(Z_ref)) * (uf_out_tot - Z_ref * if_out_tot)

s11 = (b1 / a1)
s21 = (b2 / a1)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(freq/1e9, 20*log10(abs(s11)), 'k-', linewidth=2, label='$S_{11}$')
ax1.plot(freq/1e9, 20*log10(abs(s21)), 'r--', linewidth=2, label='$S_{21}$')
ax1.set_xlabel('frequency [Hz]')
ax1.set_ylabel('S11', color='k')
ax2.set_ylabel('S21', color='r')
ax2.set_ylim(ax1.get_ylim())
plt.savefig(os.path.join(Plot_Path, 's_parameters.pdf'))
plt.show()