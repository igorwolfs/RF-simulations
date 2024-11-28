# -*- coding: utf-8 -*-
"""
 Simple Patch Antenna Tutorial

 Tested with
  - python 3.10
  - openEMS v0.0.34+

 (c) 2015-2023 Thorsten Liebig <thorsten.liebig@gmx.de>

"""

### Import Libraries
import os, tempfile
from pylab import *

from CSXCAD  import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import *

import shutil

APPCSXCAD_CMD = '~/opt/openEMS/bin/AppCSXCAD'
sim_enabled = True


### CONSTANTS
from openEMS.physical_constants import *
unit = 1e-3 # specify everything in um

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

### FDTD setup
CSX = ContinuousStructure()
## * Limit the simulation to 30k timesteps
## * Define a reduced end criteria of -40dB
max_timesteps = 30000
end_criteria = 1e-4
FDTD = openEMS(NrTS=max_timesteps, EndCriteria=end_criteria)
FDTD.SetCSX(CSX)

#######################################################################################################################################
# BOUNDARY CONDITIONS
#######################################################################################################################################
FDTD.SetBoundaryCond( ['MUR', 'MUR', 'MUR', 'MUR', 'MUR', 'MUR'] )

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
# setup FDTD parameter & excitation function
f0 = 2e9 # center frequency
fc = 1e9 # 20 dB corner frequency

FDTD.SetGaussExcite( f0, fc )


#######################################################################################################################################
# MATERIALS
#######################################################################################################################################
materialList = {}

## CREATE PATCH MATERIAL
materialList['patch'] = CSX.AddMetal( 'patch' ) # create a perfect electric conductor (PEC)
patch_dy = 60
patch_dl = 60
patch_dz = 1.524
## CREATE GROUND PLANE
materialList['gnd'] = CSX.AddMetal( 'gnd' ) # create a perfect electric conductor (PEC)

## SUBSTRATE
substrate_epsR   = 3.38
substrate_kappa  = 1e-3 * 2*pi*2.45e9 * EPS0*substrate_epsR
materialList['substrate'] = CSX.AddMaterial( 'substrate', epsilon=substrate_epsR, kappa=substrate_kappa)

# patch width (resonant length) in x-direction
patch_width  = 32 #
# patch length in y-direction
patch_length = 40

#substrate setup
substrate_width  = 60
substrate_length = 60
substrate_thickness = 1.524

# size of the simulation box
SimBox = np.array([200, 200, 150])

wavelength_min = (C0/(f0+fc))
wavelength_min_u = wavelength_min / unit
mesh_res = wavelength_min/20

### Generate properties, primitives and mesh-grid
#initialize the mesh with the "air-box" dimensions

mesh.x = np.concatenate((mesh.x, np.array([-SimBox[0]/2, SimBox[0]/2])))
mesh.y = np.concatenate((mesh.y, np.array([-SimBox[1]/2, SimBox[1]/2])))
mesh.z = np.concatenate((mesh.z, np.array([-SimBox[2]/3, SimBox[2]*2/3])))

#######################################################################################################################################
# Geometry and Grid
#######################################################################################################################################

##! DEFINING BOXES
# create patch
start_patch = [-patch_width/2, -patch_length/2, substrate_thickness]
stop_patch  = [ patch_width/2 , patch_length/2, substrate_thickness]
materialList['patch'].AddBox(priority=10, start=start_patch, stop=stop_patch) # add a box-primitive to the metal property 'patch'


# FDTD.AddEdges2Grid(dirs='xy', properties=materialList['patch'], metal_edge_res=mesh_res/2)
third_array = np.array([-mesh_res / 3, 2 * mesh_res / 3]) / 2
mesh.x = np.concatenate((mesh.x, start_patch[0] + third_array, stop_patch[0] - third_array))
mesh.y = np.concatenate((mesh.y, start_patch[1] + third_array, stop_patch[1] - third_array))

# create substrate
start_subs = [-substrate_width/2, -substrate_length/2, 0]
stop_subs  = [ substrate_width/2,  substrate_length/2, substrate_thickness]
materialList['substrate'].AddBox( priority=0, start=start_subs, stop=stop_subs)



# apply the excitation & resist as a current source
feed_pos = -6 # feeding position in x-direction
feed_R = 50     #feed resistance

start_port = [feed_pos, 0, 0]
stop_port  = [feed_pos, 0, substrate_thickness]
port = FDTD.AddLumpedPort(1, feed_R, start_port, stop_port, 'z', 1.0, priority=5, edges2grid='xy')

##! DEFINING GRID
from CSXCAD.SmoothMeshLines import SmoothMeshLines

# add extra cells to discretize the substrate thickness

mesh.z = np.concatenate((mesh.z, linspace(0,substrate_thickness,5)))

# create ground (same size as substrate)
start_gnd = [-substrate_width/2, -substrate_length/2, 0]
stop_gnd = [substrate_width/2, substrate_length/2, substrate_thickness]
materialList['gnd'].AddBox(start_gnd, stop_gnd, priority=10)

mesh.x = np.concatenate((mesh.x, np.array([start_gnd[0], stop_gnd[0]])))
mesh.y = np.concatenate((mesh.y, np.array([start_gnd[1], stop_gnd[1]])))


mesh.x = SmoothMeshLines(mesh.x, mesh_res, 1.4)
mesh.y = SmoothMeshLines(mesh.x, mesh_res, 1.4)
mesh.z = SmoothMeshLines(mesh.x, mesh_res, 1.4)

openEMS_grid.AddLine('x', mesh.x)
openEMS_grid.AddLine('y', mesh.y)
openEMS_grid.AddLine('z', mesh.z)


#######################################################################################################################################
# PORTS
#######################################################################################################################################

# Add the nf2ff recording box
nf2ff = FDTD.CreateNF2FFBox()

### Run the simulation
CSX_file = os.path.join(Sim_Path, 'simp_patch.xml')
if not os.path.exists(Sim_Path):
    os.mkdir(Sim_Path)
CSX.Write2XML(CSX_file)
from CSXCAD import AppCSXCAD_BIN
os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

if sim_enabled:
	FDTD.Run(Sim_Path, cleanup=True, debug_material=True, debug_pec=True, debug_operator=True, debug_boxes=True, debug_csx=True, verbose=3)

Sim_Path
#######################################################################################################################################
# POST_PROCESSING
#######################################################################################################################################
### Run the simulation

f = np.linspace(max(1e9,f0-fc),f0+fc,401)
port.CalcPort(Sim_Path, f)
s11 = port.uf_ref/port.uf_inc
s11_dB = 20.0*np.log10(np.abs(s11))
figure()
plot(f/1e9, s11_dB, 'k-', linewidth=2, label='$S_{11}$')
grid()
legend()
ylabel('S-Parameter (dB)')
xlabel('Frequency (GHz)')

idx = np.where((s11_dB<-10) & (s11_dB==np.min(s11_dB)))[0]
if not len(idx)==1:
    print('No resonance frequency found for far-field calulation')
else:
    f_res = f[idx[0]]
    theta = np.arange(-180.0, 180.0, 2.0)
    phi   = [0., 90.]
    nf2ff_res = nf2ff.CalcNF2FF(Sim_Path, f_res, theta, phi, center=[0,0,1e-3])

    figure()
    E_norm = 20.0*np.log10(nf2ff_res.E_norm[0]/np.max(nf2ff_res.E_norm[0])) + 10.0*np.log10(nf2ff_res.Dmax[0])
    plot(theta, np.squeeze(E_norm[:,0]), 'k-', linewidth=2, label='xz-plane')
    plot(theta, np.squeeze(E_norm[:,1]), 'r--', linewidth=2, label='yz-plane')
    grid()
    ylabel('Directivity (dBi)')
    xlabel('Theta (deg)')
    title('Frequency: {} GHz'.format(f_res/1e9))
    legend()

Zin = port.uf_tot/port.if_tot
figure()
plot(f/1e9, np.real(Zin), 'k-', linewidth=2, label='$\Re\{Z_{in}\}$')
plot(f/1e9, np.imag(Zin), 'r--', linewidth=2, label='$\Im\{Z_{in}\}$')
grid()
legend()
ylabel('Zin (Ohm)')
xlabel('Frequency (GHz)')

show()
