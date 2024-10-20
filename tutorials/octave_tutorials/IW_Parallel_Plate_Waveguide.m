#############################################################################################
##################################### PATHS ADDED ###########################################
#############################################################################################

addpath('~/opt/openEMS/share/openEMS/matlab');
addpath('~/opt/openEMS/share/CSXCAD/matlab');
addpath('~/opt/openEMS/share/hyp2mat/matlab');

close all
clear
clc

save_folder = 'sinusoidal';


###############################################################################################
###################################### SET CONSTANTS ###########################################
###############################################################################################

physical_constants;
unit = 1e-3; % drawing unit in mm, should be passed whenever creating a grid

### FREQUENCY
f_start = 1e9;
f0 = 1.5e9;
f_stop = 2e9;
lambda0 = (c0/f0)/unit; % Number of discrete steps for 1 wavelength
display("wavelength per mm");
display(lambda0);
% lambda0 is 200 mm for 1.5 GHz -> So make the plates x: 2 times lambda and the Z: 4 times lambda
% and the y 1 times lambda in both directions
mesh_res = lambda0 ./ [30 30 30] % Make sure there are 30 mesh-steps per wavelength

% 6 mm per grid: 6*30 = 180 is 1 wavelength

### PLATE DIMENSIONS (in units)
plate_x = [-200 200];
plate_y = [-100 100];
plate_z = [-600 600];

###############################################################################################
###################################### INITIALIZE FDTD ###########################################
###############################################################################################

% init and define FDTD parameter
# 50: force given timestep?
% init and define FDTD parameter: oversampled at a factor 50 x the nyquist rate

%{
<<< DEFAULT VALUES >>>
- NrTS: number of time samples
%}
FDTD = InitFDTD('NrTS', 100, 'EndCriteria', 0, 'OverSampling',50);

#############################################################################################
################################# BOUNDARY CONDITIONS #######################################
#############################################################################################

# ---> [xmin, xmax, ymin, ymax, zmin, zmax] <---
# Parallel plate waveguide: on ymin and ymax there's a PEC.
# Excitation happens in the y-direction, in the xy plane.
% BC = {'PMC' 'PMC' 'PEC' 'PEC' 'MUR' 'MUR'};
BC = {'PMC' 'PMC' 'PEC' 'PEC' 'MUR' 'MUR'};
FDTD = SetBoundaryCond(FDTD,BC);

#####################################################################################
################################# GRID / MESH #######################################
#####################################################################################

% init and define FDTD mesh
CSX = InitCSX();
# Mesh goes from -10 -> 10
% SmoothMeshLines( lines, max_res, ratio, varargin)

% Distance between plates:
display("Mesh Resolution:");
display(mesh_res);

mesh.x = SmoothMeshLines(plate_x, mesh_res(1));
mesh.y = SmoothMeshLines(plate_y, mesh_res(2));
mesh.z = SmoothMeshLines(plate_z, mesh_res(3));

CSX = DefineRectGrid(CSX, unit, mesh);

####################################################################################
################################# EXCITATION #######################################
####################################################################################

%{
### Q: CHANGING EXCITATION TO HIGHER FREQUENCY
Make sure your mesh is small enough
- 
%}

# 10 MHz Sinusoidal excitation
FDTD = SetSinusExcite(FDTD,f0); # SINUSOIDAL EXCITATION
% FDTD = SetGaussExcite(FDTD, 1e9, 1e6); # WAVELET EXCITATION

% define the excitation
% Excitation rectangle in the xy-plane.
start = [mesh.x(1), mesh.y(1), 0];
stop = [mesh.x(end), mesh.y(end), 0];

display("excitation: ")
display(start);
display(stop);
% 0: soft field excitation, [0 1 0]: excitation in y-direction?
CSX = AddExcitation(CSX, 'excitation', 0, [0 1 0]);
% 0: soft field excitation, start, stop -> where the excitation starts and where it stops
% Question: how do I know the material of the grid?
CSX = AddBox(CSX,'excitation', 0, start, stop);

####################################################################################
#################################### DUMPS #########################################
####################################################################################

% define a time domain e-field dump box
start = [mesh.x(1) 0 mesh.z(1)];
stop = [mesh.x(end) 0 mesh.z(end)];

display("dump: ")
display(start);
display(stop);

CSX = AddDump(CSX,'Et','DumpMode',0);
CSX = AddBox(CSX,'Et',0, start, stop);

% CSX = AddDump(CSX,'Ht','DumpMode',1)
% CSX = AddBox(CSX,'Et',0,[-10 0 -10],[10 0 30]);

% CSX = AddDump(CSX,'It', 'DumpMode',2);
% CSX = AddBox(CSX,'Et',0,[-10 0 -10],[10 0 30]);

% CSX = AddDump(CSX, 'rotH', 'DumpMode',3);
% CSX = AddBox(CSX,'Et',0,[-10 0 -10],[10 0 30]);

% CSX = AddDump(CSX, 'Dt', 'DumpMode',4);
% CSX = AddBox(CSX,'Et',0,[-10 0 -10],[10 0 30]);

% CSX = AddDump(CSX, 'Bt', 'DumpMode',5);
% CSX = AddBox(CSX,'Et',0,[-10 0 -10],[10 0 30]);

% CSX = AddDump(CSX,'Ef','DumpMode',10);
% CSX = AddBox(CSX,'Et',0,[-10 0 -10],[10 0 30]);

% CSX = AddDump(CSX,'Hf','DumpMode',11);
% CSX = AddBox(CSX,'Et',0,[-10 0 -10],[10 0 30]);

# Add the electric field in the xz plane
# *Q*: Why would you need to add the elctric field here?
# - 

% remove old simulation results (if exist)
rmdir(save_folder,'s');mkdir(save_folder);

% write openEMS xml data file
WriteOpenEMS(strcat(save_folder,'/tmp.xml'),FDTD,CSX);

% view defined structure
CSXGeomPlot(strcat(save_folder,'/tmp.xml'));

% run openEMS simulation
RunOpenEMS(save_folder,'tmp.xml','');

disp('use Paraview to visualize the FDTD result...');

#######################################################################################
#################################### COMMENTS #########################################
#######################################################################################
%{
### LAUNCH
At launch don't forget to: "unset GTK_PATH", in order to be able to run octave

### PASSING PARAMETERS
The way openEMS works is the parameters coming always needs to be indicated by the "string-name" of the parameter.
e.g.: "oversampling", 50 -> means oversampling needs to be done at a multiple of 50 of the nyquist frequency.


### SIMULATION TOO SLOW
Try to reduce the simulation grid, excitation etc.. size.

### GRID SIZE INCORRECT
The grid size for some reason shows only 12 or 6 lines. The gridding isn't correct.

### TIME STEP INCORRECT
The speed of light is: 299792458 m/s, 
- Which means 1 m is travelled in 3.33564095e-9, and half of that for 500 mm
So obviously the length of the timestep needs to be smaller, or the grid needs to be larger than that.
The timestep seemed to be needs to be obviously smaller than 
FDTD timestep is: 1.92308e-09 s; Nyquist rate: 25 timesteps @1.04e+07 Hz

### ERROR RETURN 137
Means that the linux memory maanger sent SIGKILL to your process because it used to much memory
== check "cat /var/log/syslog", which shows in this case
> Oct 15 16:22:47 Igor kernel: [21770.664249] Out of memory: Killed process 55834 (openEMS) total-vm:10425436kB, anon-rss:9135488kB, file-rss:224kB, shmem-rss:0kB, UID:1000 pgtables:18200kB oom_score_adj:0
Which shows 10.425436 Gb (more than 16 Gb we have)
%}