'''
# * GOAL:
Recreate the S-parameter results of the MSL port without using an MSL port.

# * RESULT:
'''


### Import Libraries
import os, tempfile
from pylab import *
import shutil
from CSXCAD  import ContinuousStructure
from openEMS import openEMS

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'

sim_enabled = True

### CONSTANTS
from openEMS.physical_constants import *
unit = 1e-6 # specify everything in um

## SIMULATION FOLDER SETUP
currDir = os.getcwd()
file_name = os.path.basename(__file__).strip('.py')
Plot_Path = os.path.join(currDir, file_name)
Sim_Path = os.path.join(Plot_Path, file_name)
if sim_enabled:
	if not (os.path.exists(Plot_Path)):
		os.mkdir(Plot_Path)
		os.mkdir(Sim_Path)
	else:
		shutil.rmtree(Sim_Path)
		os.mkdir(Sim_Path)


## setup FDTD parameter & excitation function
CSX = ContinuousStructure()
min_decrement = 1e-5 # equivalent to -50 dB
FDTD = openEMS(EndCriteria=min_decrement)
FDTD.SetCSX(CSX)
#######################################################################################################################################
# BOUNDARY CONDITIONS
#######################################################################################################################################
# FDTD.SetBoundaryCond( ['MUR', 'MUR', 'MUR', 'MUR', 'PEC', 'MUR'] )
# FDTD.SetBoundaryCond( ['PEC', 'PEC', 'PEC', 'PEC', 'PEC', 'PEC'] )

FDTD.SetBoundaryCond( ['PML_8', 'PML_8', 'MUR', 'MUR', 'PEC', 'MUR'] )

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
# EXCITATION Gaussian
#######################################################################################################################################
f_max = 7e9
f0 = f_max / 2
fc = f_max / 2
FDTD.SetGaussExcite(f0, fc)


#######################################################################################################################################
# MATERIALS
#######################################################################################################################################

materialList = {}

## MATERIAL - PEC
materialList['PEC'] = CSX.AddMetal( 'PEC' )
MSL_dx = 50000*2*2 # 5 cm
MSL_dy = 600 # 0.6 mm
stub_dy = 17e3 # 12 mm


## MATERIAL - RO4350B
substrate_eps = 3.66
substrate_dz = 254
materialList['RO4350B'] = CSX.AddMaterial( 'RO4350B', epsilon=substrate_eps)

wavelength_min = (C0/f0) *  (1/(sqrt(substrate_eps)))
wavelength_min_u = wavelength_min / unit
resolution_u = wavelength_min_u / 50 # resolution of lambda / 50

#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################
from CSXCAD.SmoothMeshLines import SmoothMeshLines

## PEC STUB DEFINITION (the XY-plane)
start_pec_stub = [MSL_dx/2-MSL_dy/2,  MSL_dy/2, substrate_dz]
stop_pec_stub  = [MSL_dx/2+MSL_dy/2,  MSL_dy/2+stub_dy, substrate_dz]
materialList['PEC'].AddBox(start_pec_stub, stop_pec_stub, priority=10)


start_pec = [0,  -MSL_dy/2, substrate_dz]
stop_pec  = [MSL_dx,  MSL_dy/2, substrate_dz]
materialList['PEC'].AddBox(start_pec, stop_pec, priority=10)

## DIELECTRIC DEFINITION
subs_start = [0, -15*MSL_dy, 0]
subs_stop  = [MSL_dx, +15*MSL_dy+stub_dy, substrate_dz]
subs_priority = 0
materialList['RO4350B'].AddBox(subs_start, subs_stop, priority=subs_priority)


## EXCITATION DEFINITION
print(f"WARNING, THE Excitation here might not be on a grid")
port_dx = 10*resolution_u
exc_start = [port_dx, -MSL_dy/2 , substrate_dz]
exc_stop  = [port_dx,  MSL_dy/2 , 0]
exc_priority = 10
excitation = CSX.AddExcitation('excite', exc_type=0, exc_val=[0, 0, -1])
excitation.AddBox(exc_start, exc_stop, priority=exc_priority)


## * Do manual meshing X-DIR
third_mesh = array([2*resolution_u/3, -resolution_u/3])/4
# Add 2/3rds x resolution on the outside and 1/3rd x resolution on the inside of the MSL
mesh.x = np.concatenate((mesh.x, np.array([MSL_dx/2]), MSL_dx/16+MSL_dy/2+third_mesh, MSL_dx/2-MSL_dy/2-third_mesh))
# Add mesh resolution to current / voltage probe location
mesh.x = np.concatenate((mesh.x, np.array([MSL_dx/4, MSL_dx*3/4])))
mesh.x = SmoothMeshLines(mesh.x, resolution_u/4)

## Add mesh around excitation
mesh.x = np.concatenate((mesh.x, np.array([port_dx]), port_dx+third_mesh, port_dx-third_mesh))

# Add X-edges to the simulation
mesh.x = np.concatenate((mesh.x, np.array([0, MSL_dx])))
mesh.x = SmoothMeshLines(mesh.x, resolution_u)

## * Do manual meshing Y-DIR
# Add 2/3rds x resolution on the outside and 1/3rd x resolution on the inside of the MSL
mesh.y = np.concatenate((mesh.y, np.array([0.0]), MSL_dy/2+third_mesh, -MSL_dy/2-third_mesh))
mesh.y = SmoothMeshLines(mesh.y, resolution_u/4)
mesh.y = np.concatenate((mesh.y, (MSL_dy/2+stub_dy)+third_mesh))

# Add edges in Y-edges to simulation 
mesh.y = np.concatenate((mesh.y, np.array([-15*MSL_dy, 15*MSL_dy+stub_dy])))
mesh.y = SmoothMeshLines(mesh.y, resolution_u)

# Create 5 points from 0 to substrate_dz
mesh.z = np.concatenate((mesh.z, linspace(0, substrate_dz, 5)))

# Z2 boundary condition is MUR, 3000 -> 3 mm
mesh.z = np.concatenate((mesh.z, np.array([3000])))
mesh.z = SmoothMeshLines(mesh.z, resolution_u)



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

### * Grid functions for interpolation
interpl_x  = interp1d( mesh.x, np.arange(0,mesh.x.size, 1), kind='nearest', fill_value="extrapolate")
interpl_y  = interp1d( mesh.y, np.arange(0,mesh.y.size, 1), kind='nearest', fill_value="extrapolate")
interpl_z  = interp1d( mesh.z, np.arange(0,mesh.z.size, 1), kind='nearest', fill_value="extrapolate")

xdelta = diff(mesh.x)
ydelta = diff(mesh.y)
zdelta = diff(mesh.z)

### * PORT IN
in_xidx =  int(interpl_x(MSL_dx/6)) #MSL_dx/4)) 		# length / 4
in_yidx1 = int(interpl_y(-MSL_dy/2)) 	# width / 2
in_yidx2 = int(interpl_y(MSL_dy/2)) 	# width / 2
in_zidx = int(interpl_z(substrate_dz)) 	# height


## define voltage calc box
dump_boxes['in_ut1'] = CSX.AddProbe(  'in_ut1', 0 )
in_ut1_start = [mesh.x[in_xidx], 0, substrate_dz]
in_ut1_stop  = [mesh.x[in_xidx], 0, 0]
dump_boxes['in_ut1'].AddBox(in_ut1_start, in_ut1_stop, priority=0)

# add a second voltage probe to compensate space offset between voltage and current
dump_boxes['in_ut2'] = CSX.AddProbe(  'in_ut2', 0 )
in_ut2_start = [mesh.x[in_xidx+1], 0, substrate_dz]
in_ut2_stop  = [mesh.x[in_xidx+1], 0, 0]
dump_boxes['in_ut2'].AddBox(in_ut2_start, in_ut2_stop, priority=0)

## define current calc box
# current calc boxes will automatically snap to the next dual mesh-line
dump_boxes['in_it1'] = CSX.AddProbe( 'in_it1', p_type=1, weight=1, norm_dir= 0)
in_start_it1 = [mesh.x[in_xidx]+xdelta[in_xidx]/2, mesh.y[in_yidx1]-ydelta[in_yidx1-1]/2, mesh.z[in_zidx]]
in_stop_it1  = [mesh.x[in_xidx]+xdelta[in_xidx]/2, mesh.y[in_yidx2]+ydelta[in_yidx2]/2  , mesh.z[in_zidx]]
print(f"in_start_i1: {in_start_it1}")
print(f"in_stop_it1: {in_stop_it1}")
dump_boxes['in_it1'].AddBox(in_start_it1, in_stop_it1, priority=0)

### * PORT OUT
out_xidx  = int(interpl_x(MSL_dx - MSL_dx/6)) #int(interpl_x(MSL_dx*3/4))   # length / 4
out_yidx1 = int(interpl_y(-MSL_dy/2))    # width / 2
out_yidx2 = int(interpl_y(MSL_dy/2))     # width / 2
out_zidx  = int(interpl_z(substrate_dz)) # height

## define voltage calc box
dump_boxes['out_ut1'] = CSX.AddProbe(  'out_ut1', 0 )
out_ut1_start = [mesh.x[out_xidx], 0, substrate_dz]
out_ut1_stop  = [mesh.x[out_xidx], 0, 0]
dump_boxes['out_ut1'].AddBox(out_ut1_start, out_ut1_stop, priority=0)

# add a second voltage probe to compensate space offset between voltage and current
dump_boxes['out_ut2'] = CSX.AddProbe(  'out_ut2', 0 )
out_ut2_start = [mesh.x[out_xidx+1], 0, substrate_dz]
out_ut2_stop  = [mesh.x[out_xidx+1], 0, 0]
dump_boxes['out_ut2'].AddBox(out_ut2_start, out_ut2_stop, priority=0)

## define current calc box
# current calc boxes will automatically snap to the next dual mesh-line (propagation direction)
'''
@brief: AddProbe
@param: p_type: probe-type, 1: current sensing, 0: voltage sensing
@param: weight: weighting factor of the current, should be -1 for output port, 1 for input power
@param NormDir: necessary for current probing box when dimension != 2 (measurement direction: x, y, z)
'''
dump_boxes['out_it1'] = CSX.AddProbe( 'out_it1', p_type=1, weight=-1, norm_dir= 0)
out_start_it1 = [mesh.x[out_xidx]+xdelta[out_xidx]/2, mesh.y[out_yidx1]-ydelta[out_yidx1-1]/2, mesh.z[out_zidx]]
out_stop_it1 =  [mesh.x[out_xidx]+xdelta[out_xidx]/2,  mesh.y[out_yidx2]+ydelta[out_yidx2]/2,  mesh.z[out_zidx]]
dump_boxes['out_it1'].AddBox(out_start_it1, out_stop_it1, priority=0)

## Add grid
openEMS_grid.AddLine('x', mesh.x)
openEMS_grid.AddLine('y', mesh.y)
openEMS_grid.AddLine('z', mesh.z)

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

if sim_enabled:
	FDTD.Run(Sim_Path, cleanup=True, debug_material=True, debug_pec=True, debug_operator=True, debug_boxes=True, debug_csx=True, verbose=3)

#######################################################################################################################################
# POST_PROCESSING
#######################################################################################################################################
### Run the simulation

from openEMS.ports import UI_data
freq = linspace( f0-fc, f0+fc, 1601)
# freq = linspace( 1e6, f0, 1601 )

E_field = UI_data(['et'], Sim_Path, freq)
U_in = UI_data(['in_ut1', 'in_ut2'], Sim_Path, freq) # Time domain/freq domain voltage
U_out = UI_data(['out_ut1', 'out_ut2'], Sim_Path, freq) # Time domain/freq domain voltage
I_in = UI_data(['in_it1'], Sim_Path, freq) # time domain / freq domain current (half time step offset is corrected? in octave?)
I_out = UI_data(['out_it1'], Sim_Path, freq) # time domain / freq domain current (half time step offset is corrected? in octave?)


## Characteristic impedance calculation
# input
uf_in_tot = (U_in.ui_f_val[0] + U_in.ui_f_val[1]) / 2
if_in_tot = I_in.ui_f_val[0]

# output
uf_out_tot = (U_out.ui_f_val[0] + U_out.ui_f_val[1]) / 2
if_out_tot = I_out.ui_f_val[0]

## S-Parameters
# MSL Length: 100 mm
# eps: 3.66
Z_ref = 50.0


### * CALCULATIONS AS DONE IN THE MSLPort-CLASS
# uf_in_inc = 0.5 * (uf_in_tot + if_in_tot * Z_ref)
# if_in_inc = 0.5 * (if_in_tot + uf_in_tot / Z_ref)

# uf_in_ref = uf_in_tot - uf_in_inc
# if_in_ref = if_in_inc - if_in_tot


# uf_out_inc = 0.5 * (uf_out_tot + if_out_tot * Z_ref)
# if_out_inc = 0.5 * (if_out_tot + uf_out_tot / Z_ref)

# uf_out_ref = uf_out_tot - uf_out_inc
# if_out_ref = if_out_inc - if_out_tot

# s11 = uf_in_ref / uf_in_inc
# s21 = uf_out_ref / uf_in_inc

## Excitation applied at port 1 only:
a1 = 1/(2*sqrt(Z_ref)) * (uf_in_tot + Z_ref * I_in.ui_f_val[0])
b1 = 1/(2*sqrt(Z_ref)) * (uf_in_tot - Z_ref * I_in.ui_f_val[0])
a2 = 1/(2*sqrt(Z_ref)) * (uf_out_tot + Z_ref * I_out.ui_f_val[0])
b2 = 1/(2*sqrt(Z_ref)) * (uf_out_tot - Z_ref * I_out.ui_f_val[0])

s11 = (b1 / a1)
s21 = (b2 / a1)

## Expected peaks
'''
Calculate the expected reflected peaks for a stub of length "stub_dy".
-> expected reflections occur at lambda * (2*n+1)/4, with n a natural number 
'''
res_freq_list = []
res_freq = (C0 / sqrt(substrate_eps)) / (4*stub_dy * unit)
while (res_freq < f0+fc):
	res_freq_list.append(res_freq)
	res_freq = ((C0 / sqrt(substrate_eps)) / (4*stub_dy * unit / (len(res_freq_list)*2+1)))
	print(f"res_freq: {res_freq}, max: {f0+fc}")

print(f"freq_list: {res_freq_list}")
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(freq/1e9, 20*log10(abs(s11)), 'k-', linewidth=2, label='$S_{11}$')
ax1.plot(freq/1e9, 20*log10(abs(s21)), 'r--', linewidth=2, label='$S_{21}$')
ax1.plot(np.array(res_freq_list)/1e9, np.zeros_like(res_freq_list), 'bo', label='expected peak')
ax1.set_xlabel('frequency [Hz]')
ax1.set_ylabel('S11', color='k')
ax2.set_ylabel('S21', color='r')
ax2.set_ylim(ax1.get_ylim())
plt.savefig(os.path.join(Plot_Path, 's_parameters.pdf'))
plt.show()


'''
## IMPEDANCE
Z_in = uf_in_tot / if_in_tot
Z_out = uf_out_tot / if_out_tot

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(freq*1e-6, abs(Z_in), 'g-', linewidth=2, label='$\Z_in\{Z\}$')
ax1.plot(freq*1e-6, abs(Z_out), 'b-', linewidth=2, label='$\Z_out\{Z\}$')
ax1.set_xlabel('frequency [Hz]')
ax1.set_ylabel('Z_in [Ohm]', color='g')
ax2.set_ylabel('Z_out [Ohm]', color='b')
ax2.set_ylim(ax1.get_ylim())
plt.savefig(os.path.join(Plot_Path, 'impedance.pdf'))
plt.show()


## Plotting
# * figure()
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax3 = ax1.twinx()
ax1.plot(U_in.ui_time[0], U_in.ui_val[0], 'g-', linewidth=2, label='$in_ut$')
ax2.plot(U_out.ui_time[0], U_out.ui_val[0], 'b-', linewidth=2, label='$out_ut$')
ax3.plot(E_field.ui_time[0], E_field.ui_val[0], 'y-', linewidth=2)

ax1.set_xlabel('time (t / ns)')
ax1.set_ylabel('Volts (V)', color='g')
ax2.set_ylabel('Volts (V)', color='b')

plt.savefig(os.path.join(Plot_Path, 'voltages.pdf'))
plt.show()


## UF_TOT DEBUGGING PLOTS
figure()
plot(freq*1e-6, uf_in_tot, linewidth=2, label='$uf_tot_portin$')
grid()
plot(freq*1e-6, uf_out_tot, linewidth=2, label='$uf_tot_portout$')
ylabel('uf_tot')
xlabel(r'frequency (MHz) $\rightarrow$')
legend()

plt.savefig(os.path.join(Plot_Path, 'uf_tot.pdf'))
show()

## IF_TOT DEBUGGING PLOTS
figure()
plot(freq*1e-6, if_in_tot, linewidth=2, label='$if_tot_portin$')
grid()
plot(freq*1e-6, if_out_tot, linewidth=2, label='$if_tot_portout$')
ylabel('if_tot')
xlabel(r'frequency (MHz) $\rightarrow$')
legend()

plt.savefig(os.path.join(Plot_Path, 'if_tot.pdf'))
show()
'''