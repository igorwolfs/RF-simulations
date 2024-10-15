#############################################################################################
##################################### PATHS ADDED ###########################################
#############################################################################################


addpath('~/opt/openEMS/share/openEMS/matlab');
addpath('~/opt/openEMS/share/CSXCAD/matlab');
addpath('~/opt/openEMS/share/hyp2mat/matlab');

close all
clear
clc


save_folder = "test";


###############################################################################################
###################################### SET CONSTANTS ###########################################
###############################################################################################
physical_constants;
unit = 1;

### FREQUENCY
f0 = 10e6;
lambda0 = (c0/f0)/unit; % Number of discrete steps for 1 wavelength
% display("wavelength per m");
% display(lambda0);

mesh_res = [1 1 1];
### PLATE DIMENSIONS
plate_x = [-10 10];
plate_y = [-10 10];
plate_z = [-10 30];

###############################################################################################
###################################### INITIALIZE FDTD ########################################
###############################################################################################

% init and define FDTD parameter
% FDTD = InitFDTD(100,0,'OverSampling',50);
FDTD = InitFDTD('NrTS', 100, 'EndCriteria', 0, 'OverSampling',50);

#############################################################################################
################################# BOUNDARY CONDITIONS #######################################
#############################################################################################

BC = {'PMC' 'PMC' 'PEC' 'PEC' 'MUR' 'MUR'};
FDTD = SetBoundaryCond(FDTD, BC);

#####################################################################################
################################# GRID / MESH #######################################
#####################################################################################

% init and define FDTD mesh
CSX = InitCSX();

% Distance between plates:
% display("Mesh Resolution:");
% display(mesh_res);

mesh.x = SmoothMeshLines(plate_x, mesh_res(1));
mesh.y = SmoothMeshLines(plate_y, mesh_res(2));
mesh.z = SmoothMeshLines(plate_z, mesh_res(3));

CSX = DefineRectGrid(CSX, unit, mesh);

####################################################################################
################################# EXCITATION #######################################
####################################################################################

FDTD = SetSinusExcite(FDTD, f0);
% define the excitation
start = [mesh.x(1), mesh.y(1), 0];
stop = [mesh.x(end), mesh.y(end), 0];

% display("excitation: ")
% display(start);
% display(stop);

CSX = AddExcitation(CSX,'excitation', 0, [0 1 0]);
CSX = AddBox(CSX,'excitation',0, start, stop);


####################################################################################
#################################### DUMPS #########################################
####################################################################################

start = [mesh.x(1) 0 mesh.z(1)];
stop = [mesh.x(end) 0 mesh.z(end)];

% display("dump: ")
% display(start);
% display(stop);

CSX = AddDump(CSX, 'Et', 'DumpMode', 0);
CSX = AddBox(CSX,'Et', 0, start, stop);

% remove old simulation results (if exist)
rmdir(save_folder,'s');mkdir(save_folder);

% write openEMS xml data file
WriteOpenEMS(strcat(save_folder,'/test.xml'),FDTD,CSX);

% view defined structure
% CSXGeomPlot(strcat(save_folder,'/test.xml'));

% run openEMS simulation
RunOpenEMS(save_folder,'test.xml','-vvv');
% RunOpenEMS(save_folder,'test.xml');

disp('use Paraview to visualize the FDTD result...');