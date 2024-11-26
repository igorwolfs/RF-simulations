'''
# * GOAL:
Get the stripline example from theliebig.

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
# min_decrement = 1e-5 # equivalent to -50 dB
max_steps = 6000
FDTD = openEMS(NrTS=max_steps)
FDTD.SetCSX(CSX)
#######################################################################################################################################
# BOUNDARY CONDITIONS
#######################################################################################################################################
# FDTD.SetBoundaryCond( ['MUR', 'MUR', 'MUR', 'MUR', 'PEC', 'MUR'] )
# FDTD.SetBoundaryCond( ['PEC', 'PEC', 'PEC', 'PEC', 'PEC', 'PEC'] )

FDTD.SetBoundaryCond( ['PML_8', 'PML_8', 'PMC', 'PMC', 'PEC', 'PEC'] )

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
SL_dx = 50e3 # 50 mm
SL_dy = 520 # 520 um mm
SL_dz = 0 # 500 um mm


## MATERIAL - RO4350B
substrate_eps = 3.66
materialList['RO4350B'] = CSX.AddMaterial( 'RO4350B', epsilon=substrate_eps)
substrate_dx = SL_dx
substrate_dy = SL_dy*20
substrate_dz = 1000

## WAVELENGTH
wavelength_min = (C0/f0) *  (1/(sqrt(substrate_eps)))
wavelength_min_u = wavelength_min / unit
resolution_u = wavelength_min_u / 50 # resolution of lambda / 50

#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################
from CSXCAD.SmoothMeshLines import SmoothMeshLines

## START PEC
start_pec = [0,     -SL_dy/2, 0]
stop_pec  = [SL_dx,  SL_dy/2, 0]
materialList['PEC'].AddBox(start_pec, stop_pec, priority=10)

## DIELECTRIC DEFINITION
subs_start = [0,     -substrate_dy/2, -substrate_dz/2]
subs_stop  = [SL_dx,  substrate_dy/2,  substrate_dz/2]
subs_priority = 0
materialList['RO4350B'].AddBox(subs_start, subs_stop, priority=subs_priority)


#### EXCITATION DEFINITION
## UPPER EXCITATION
print(f"WARNING, THE Excitation here might not be on a grid")
port_dx = 10*resolution_u
exc_start = [port_dx, -SL_dy/2 , substrate_dz/2]
exc_stop  = [port_dx,  SL_dy/2 , 0]
exc_priority = 10
excitation = CSX.AddExcitation('excite', exc_type=0, exc_val=[0, 0, -1])
excitation.AddBox(exc_start, exc_stop, priority=exc_priority)

## LOWER EXCITATION
print(f"WARNING, THE Excitation here might not be on a grid")
port_dx = 10*resolution_u
exc_start = [port_dx, -SL_dy/2 , -substrate_dz/2]
exc_stop  = [port_dx,  SL_dy/2 , 0]
exc_priority = 10
excitation = CSX.AddExcitation('excite', exc_type=0, exc_val=[0, 0, 1])
excitation.AddBox(exc_start, exc_stop, priority=exc_priority)


## * Do manual meshing X-DIR
third_mesh = array([2*resolution_u/3, -resolution_u/3])/4

## Add mesh around excitation
mesh.x = np.concatenate((mesh.x, np.array([port_dx]), port_dx+third_mesh, port_dx-third_mesh))

# Add mesh resolution to current / voltage probe location
mesh.x = SmoothMeshLines(mesh.x, resolution_u/4)
# Add X-edges to the simulation
mesh.x = np.concatenate((mesh.x, np.array([0, SL_dx])))
mesh.x = SmoothMeshLines(mesh.x, resolution_u)

## * Do manual meshing Y-DIR
# Add 2/3rds x resolution on the outside and 1/3rd x resolution on the inside of the MSL
mesh.y = np.concatenate((mesh.y, np.array([0.0]), SL_dy/2+third_mesh, -SL_dy/2-third_mesh))
mesh.y = SmoothMeshLines(mesh.y, resolution_u/4)

# Add edges in Y-edges to simulation 
mesh.y = np.concatenate((mesh.y, np.array([-substrate_dy/2, substrate_dy/2])))
mesh.y = SmoothMeshLines(mesh.y, resolution_u)

# Create 5 points from 0 to substrate_dz
mesh.z = np.concatenate((mesh.z, linspace(0, substrate_dz/2, 5), linspace(0, -substrate_dz/2, 5)))
mesh.z = SmoothMeshLines(mesh.z, resolution_u)

print(f"xmesh: {mesh.x}")
print(f"ymesh: {mesh.y}")
print(f"zmesh: {mesh.z}")

#######################################################################################################################################
# PROBES
#######################################################################################################################################
from scipy.interpolate import interp1d


dump_boxes = {}
## define dump boxes
et_start = [mesh.x[0], mesh.y[0], 0]
et_stop  = [mesh.x[-1], mesh.y[-1], 0]
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

#! PORT IN
in_xidx =  int(interpl_x(SL_dx/4)) 		# length / 4
in_yidx1 = int(interpl_y(-SL_dy/2)) 	# width / 2
in_yidx2 = int(interpl_y(SL_dy/2)) 	# width / 2
in_zidx = int(interpl_z(0)) 	# height

## PORT UPPER
port_weight = 0.5

## define voltage calc box
dump_boxes['in_ut1_A'] = CSX.AddProbe(  'in_ut1_A', 0, weight=port_weight )
in_ut1_A_start = [mesh.x[in_xidx], 0, 0]
in_ut1_A_stop  = [mesh.x[in_xidx], 0, substrate_dz/2]
dump_boxes['in_ut1_A'].AddBox(in_ut1_A_start, in_ut1_A_stop, priority=0)

# add a second voltage probe to compensate space offset between voltage and current
dump_boxes['in_ut1_B'] = CSX.AddProbe(  'in_ut1_B', 0, weight=port_weight )
in_ut1_B_start = [mesh.x[in_xidx+1], 0, 0]
in_ut1_B_stop  = [mesh.x[in_xidx+1], 0, substrate_dz/2]
dump_boxes['in_ut1_B'].AddBox(in_ut1_B_start, in_ut1_B_stop, priority=0)

# add a third voltage probe to compensate space offset between voltage and current
dump_boxes['in_ut1_C'] = CSX.AddProbe(  'in_ut1_C', 0, weight=port_weight )
in_ut1_C_start = [mesh.x[in_xidx+2], 0, 0]
in_ut1_C_stop  = [mesh.x[in_xidx+2], 0, substrate_dz/2]
dump_boxes['in_ut1_C'].AddBox(in_ut1_C_start, in_ut1_C_stop, priority=0)

## PORT LOWER
dump_boxes['in_ut2_A'] = CSX.AddProbe(  'in_ut2_A', 0, weight=port_weight )
in_ut2_A_start = [mesh.x[in_xidx], 0, 0]
in_ut2_A_stop  = [mesh.x[in_xidx], 0, -substrate_dz/2]
dump_boxes['in_ut2_A'].AddBox(in_ut2_A_start, in_ut2_A_stop, priority=0)

# add a second voltage probe to compensate space offset between voltage and current
dump_boxes['in_ut2_B'] = CSX.AddProbe(  'in_ut2_B', 0, weight=port_weight )
in_ut2_B_start = [mesh.x[in_xidx+1], 0, 0]
in_ut2_B_stop  = [mesh.x[in_xidx+1], 0, -substrate_dz/2]
dump_boxes['in_ut2_B'].AddBox(in_ut2_B_start, in_ut2_B_stop, priority=0)

# add a third voltage probe to compensate space offset between voltage and current
dump_boxes['in_ut2_C'] = CSX.AddProbe(  'in_ut2_C', 0, weight=port_weight )
in_ut2_C_start = [mesh.x[in_xidx+2], 0, 0]
in_ut2_C_stop  = [mesh.x[in_xidx+2], 0, -substrate_dz/2]
dump_boxes['in_ut2_C'].AddBox(in_ut2_C_start, in_ut2_C_stop, priority=0)


## define current calc box
# current calc boxes will automatically snap to the next dual mesh-line
dump_boxes['in_it_A'] = CSX.AddProbe( 'in_it_A', p_type=1, weight=1, norm_dir= 0)
in_start_it_A = [mesh.x[in_xidx]+xdelta[in_xidx]/2, mesh.y[in_yidx1]-ydelta[in_yidx1-1]/2, mesh.z[in_zidx-1]]
in_stop_it_A  = [mesh.x[in_xidx]+xdelta[in_xidx]/2, mesh.y[in_yidx2]+ydelta[in_yidx2]/2  , mesh.z[in_zidx+1]]
dump_boxes['in_it_A'].AddBox(in_start_it_A, in_stop_it_A, priority=0)

dump_boxes['in_it_B'] = CSX.AddProbe( 'in_it_B', p_type=1, weight=1, norm_dir= 0)
in_start_it_B = [mesh.x[in_xidx+1]+xdelta[in_xidx+1]/2, mesh.y[in_yidx1]-ydelta[in_yidx1-1]/2, mesh.z[in_zidx-1]]
in_stop_it_B  = [mesh.x[in_xidx+1]+xdelta[in_xidx+1]/2, mesh.y[in_yidx2]+ydelta[in_yidx2]/2  , mesh.z[in_zidx+1]]
dump_boxes['in_it_B'].AddBox(in_start_it_B, in_stop_it_B, priority=0)


### * PORT OUT
out_xidx  = int(interpl_x(SL_dx - SL_dx/6)) #int(interpl_x(SL_dx*3/4))   # length / 4
out_yidx1 = int(interpl_y(-SL_dy/2))    # width / 2
out_yidx2 = int(interpl_y(SL_dy/2))     # width / 2
out_zidx  = int(interpl_z(0)) # height

## PORT UPPER
dump_boxes['out_ut1_A'] = CSX.AddProbe(  'out_ut1_A', 0, weight=port_weight)
out_ut1_A_start = [mesh.x[out_xidx], 0, 0]
out_ut1_A_stop  = [mesh.x[out_xidx], 0, substrate_dz/2]
dump_boxes['out_ut1_A'].AddBox(out_ut1_A_start, out_ut1_A_stop, priority=0)

# add a second voltage probe to compensate space offset between voltage and current
dump_boxes['out_ut1_B'] = CSX.AddProbe(  'out_ut1_B', 0, weight=port_weight )
out_ut1_B_start = [mesh.x[out_xidx+1], 0, 0]
out_ut1_B_stop  = [mesh.x[out_xidx+1], 0, substrate_dz/2]
dump_boxes['out_ut1_B'].AddBox(out_ut1_B_start, out_ut1_B_stop, priority=0)

# add a third voltage probe to compensate space offset between voltage and current
dump_boxes['out_ut1_C'] = CSX.AddProbe(  'out_ut1_C', 0, weight=port_weight )
out_ut1_C_start = [mesh.x[out_xidx+2], 0, 0]
out_ut1_C_stop  = [mesh.x[out_xidx+2], 0, substrate_dz/2]
dump_boxes['out_ut1_C'].AddBox(out_ut1_C_start, out_ut1_C_stop, priority=0)


## PORT LOWER
dump_boxes['out_ut2_A'] = CSX.AddProbe(  'out_ut2_A', 0, weight=port_weight )
out_ut2_A_start = [mesh.x[out_xidx], 0, 0]
out_ut2_A_stop  = [mesh.x[out_xidx], 0, -substrate_dz/2]
dump_boxes['out_ut2_A'].AddBox(out_ut2_A_start, out_ut2_A_stop, priority=0)

# add a second voltage probe to compensate space offset between voltage and current
dump_boxes['out_ut2_B'] = CSX.AddProbe(  'out_ut2_B', 0, weight=port_weight )
out_ut2_B_start = [mesh.x[out_xidx+1], 0, 0]
out_ut2_B_stop  = [mesh.x[out_xidx+1], 0, -substrate_dz/2]
dump_boxes['out_ut2_B'].AddBox(out_ut2_B_start, out_ut2_B_stop, priority=0)

# add a third voltage probe to compensate space offset between voltage and current
dump_boxes['out_ut2_C'] = CSX.AddProbe(  'out_ut2_C', 0, weight=port_weight )
out_ut2_C_start = [mesh.x[out_xidx+2], 0, 0]
out_ut2_C_stop  = [mesh.x[out_xidx+2], 0, -substrate_dz/2]
dump_boxes['out_ut2_C'].AddBox(out_ut2_C_start, out_ut2_C_stop, priority=0)

## define current calc box
# current calc boxes will automatically snap to the next dual mesh-line (propagation direction)
'''
@brief: AddProbe
@param: p_type: probe-type, 1: current sensing, 0: voltage sensing
@param: weight: weighting factor of the current, should be -1 for output port, 1 for input power
@param NormDir: necessary for current probing box when dimension != 2 (measurement direction: x, y, z)
'''
dump_boxes['out_it_A'] = CSX.AddProbe( 'out_it_A', p_type=1, weight=-1, norm_dir= 0)
out_start_it_A = [mesh.x[out_xidx]+xdelta[out_xidx]/2, mesh.y[out_yidx1]-ydelta[out_yidx1-1]/2, mesh.z[out_zidx-1]]
out_stop_it_A =  [mesh.x[out_xidx]+xdelta[out_xidx]/2,  mesh.y[out_yidx2]+ydelta[out_yidx2]/2,  mesh.z[out_zidx+1]]
dump_boxes['out_it_A'].AddBox(out_start_it_A, out_stop_it_A, priority=0)


dump_boxes['out_it_B'] = CSX.AddProbe( 'out_it_B', p_type=1, weight=-1, norm_dir= 0)
out_start_it_B = [mesh.x[out_xidx+1]+xdelta[out_xidx+1]/2, mesh.y[out_yidx1]-ydelta[out_yidx1-1]/2, mesh.z[out_zidx-1]]
out_stop_it_B =  [mesh.x[out_xidx+1]+xdelta[out_xidx+1]/2,  mesh.y[out_yidx2]+ydelta[out_yidx2]/2,  mesh.z[out_zidx+1]]
dump_boxes['out_it_B'].AddBox(out_start_it_B, out_stop_it_B, priority=0)


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
	print(f"Running simulation")
	FDTD.Run(Sim_Path, cleanup=True, debug_material=True, debug_pec=True, debug_operator=True, debug_boxes=True, debug_csx=True, verbose=3)
#######################################################################################################################################
# POST_PROCESSING
#######################################################################################################################################
### Run the simulation

from openEMS.ports import UI_data
freq = linspace( f0-fc, f0+fc, 1601)
# freq = linspace( 1e6, f0, 1601 )

E_field = UI_data(['et'], Sim_Path, freq)
U1_in = UI_data(['in_ut1_A', 'in_ut1_B', 'in_ut1_C'], Sim_Path, freq) # Time domain/freq domain voltage
U2_in = UI_data(['in_ut2_A', 'in_ut2_B', 'in_ut2_C'], Sim_Path, freq) # Time domain/freq domain voltage

U1_out = UI_data(['out_ut1_A', 'out_ut1_B', 'out_ut1_C'], Sim_Path, freq) # Time domain/freq domain voltage
U2_out = UI_data(['out_ut2_A', 'out_ut2_B', 'out_ut2_C'], Sim_Path, freq) # Time domain/freq domain voltage
I_in = UI_data(['in_it_A', 'in_it_B'], Sim_Path, freq) # time domain / freq domain current (half time step offset is corrected? in octave?)
I_out = UI_data(['out_it_A', 'out_it_B'], Sim_Path, freq) # time domain / freq domain current (half time step offset is corrected? in octave?)

in_i_f = []
in_u_f = []
in_u_t = []
out_u_f = []
out_u_t = []
out_i_f = []

for i in range(3):
	if (i < 2):
		in_i_f.append(I_in.ui_f_val[i])
		out_i_f.append(I_out.ui_f_val[i])
	in_u_f.append(U1_in.ui_f_val[i] + U2_in.ui_f_val[i])
	in_u_t.append(U1_in.ui_val[i] + U2_in.ui_val[i])
	out_u_f.append(U1_out.ui_f_val[i] + U2_out.ui_f_val[i])
	out_u_t.append(U1_out.ui_val[i] + U2_out.ui_val[i])

## Characteristic impedance calculation
uf_in_tot = in_u_f[1]
if_in_tot = (in_i_f[0] + in_i_f[1]) / 2
uf_out_tot = out_u_f[1]
if_out_tot = (out_i_f[0] + out_i_f[1]) / 2

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


## Expected peaks
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
# a1, a2
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(freq*1e-9, a1, 'g-', linewidth=2, label='$uf_ref_1$')
ax2.plot(freq*1e-9, a2, 'b-', linewidth=2, label='$uf_ref_2$')

ax1.set_xlabel('frequency (Hz)')
ax1.set_ylabel('Volts uf ref 1 (V)', color='g')
ax2.set_ylabel('Volts uf ref 2 (V)', color='b')

plt.savefig(os.path.join(Plot_Path, 'voltages_ref.pdf'))
plt.show()

## Frequency plot a1, a2, b1, b2

# b1, b2
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(freq*1e-9, b1, 'g-', linewidth=2, label='$uf_inc_1$')
ax2.plot(freq*1e-9, b2, 'b-', linewidth=2, label='$uf_inc_2$')

ax1.set_xlabel('frequency (Hz)')
ax1.set_ylabel('Volts uf inc 1 (V)', color='g')
ax2.set_ylabel('Volts uf inc 2 (V)', color='b')

plt.savefig(os.path.join(Plot_Path, 'voltages_inc.pdf'))
plt.show()

# uf_in_tot
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(freq*1e-9, uf_in_tot, 'g-', linewidth=2, label='$uf_in_tot$')
ax2.plot(freq*1e-9, uf_out_tot, 'b-', linewidth=2, label='$uf_out_tot$')

ax1.set_xlabel('frequency (Hz)')
ax1.set_ylabel('uf_in_tot (V)', color='g')
ax2.set_ylabel('uf_out_tot (V)', color='b')

plt.savefig(os.path.join(Plot_Path, 'uf_tot.pdf'))
plt.show()


# if_in_tot
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(freq*1e-9, if_in_tot, 'g-', linewidth=2, label='$if_in_tot$')
ax2.plot(freq*1e-9, if_out_tot, 'b-', linewidth=2, label='$if_out_tot$')

ax1.set_xlabel('frequency (GHz)')
ax1.set_ylabel('if_in_tot (A)', color='g')
ax2.set_ylabel('if_out_tot (A)', color='b')

plt.savefig(os.path.join(Plot_Path, 'if_tot.pdf'))
plt.show()

# uf_in_tot
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

ax1.plot(freq*1e-9, in_u_f[1], 'g-', linewidth=2, label='$in_u_f$')
ax2.plot(freq*1e-9, out_u_f[1], 'b-', linewidth=2, label='$out_u_f$')

ax1.set_xlabel('frequency (GHz)')
ax1.set_ylabel('in_u_f (V)', color='g')
ax2.set_ylabel('out_u_f (V)', color='b')

plt.savefig(os.path.join(Plot_Path, 'uf_raw.pdf'))
plt.show()

# f_in_tot
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(freq*1e-9, in_i_f[1], 'g-', linewidth=2, label='$in_i_f$')
ax2.plot(freq*1e-9, out_i_f[1], 'b-', linewidth=2, label='$out_i_f$')

ax1.set_xlabel('frequency (GHz)')
ax1.set_ylabel('in_i_f (V)', color='g')
ax2.set_ylabel('out_i_f (V)', color='b')

plt.savefig(os.path.join(Plot_Path, 'if_raw.pdf'))
plt.show()

'''



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