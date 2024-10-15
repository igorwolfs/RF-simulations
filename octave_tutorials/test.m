%
% Tutorials / Parallel_Plate_Waveguide
%
% Description at:
% http://openems.de/index.php/Tutorial:_Parallel_Plate_Waveguide
%
% Tested with
%  - Matlab 2011a / Octave 4.0
%  - openEMS v0.0.33
%
% (C) 2011,2012 Sebastian Held <sebastian.held@gmx.de>
% (C) 2011-2015 Thorsten Liebig <thorsten.liebig@gmx.de>
addpath('~/opt/openEMS/share/openEMS/matlab');
addpath('~/opt/openEMS/share/CSXCAD/matlab');
addpath('~/opt/openEMS/share/hyp2mat/matlab');

close all
clear
clc


save_folder = "test";

% init and define FDTD parameter
FDTD = InitFDTD(100,0,'OverSampling',50);
FDTD = SetSinusExcite(FDTD,10e6);
BC = {'PMC' 'PMC' 'PEC' 'PEC' 'MUR' 'MUR'};
FDTD = SetBoundaryCond(FDTD,BC);

% init and define FDTD mesh
CSX = InitCSX();
x_range = [-10 10];
y_range = [-10 10];
z_range = [-10 10];

mesh_res = [1 1 1];

mesh.x = -10:10;
mesh.y = -10:10;
mesh.z = -10:30;
mesh.x = SmoothMeshLines(plate_x, mesh_res(1));
mesh.y = SmoothMeshLines(plate_y, mesh_res(2));
mesh.z = SmoothMeshLines(plate_z, mesh_res(3));

CSX = DefineRectGrid(CSX, 1, mesh);

% define the excitation
CSX = AddExcitation(CSX,'excitation',0,[0 1 0]);
CSX = AddBox(CSX,'excitation',0,[-10 -10 0],[10 10 0]);

% define a time domain e-field dump box
CSX = AddDump(CSX,'Et','DumpMode',0);
CSX = AddBox(CSX,'Et',0,[-10 0 -10],[10 0 30]);

% remove old simulation results (if exist)
rmdir(save_folder,'s');mkdir(save_folder);

% write openEMS xml data file
WriteOpenEMS(strcat(save_folder,'/tmp.xml'),FDTD,CSX);

% view defined structure
CSXGeomPlot(strcat(save_folder,'/tmp.xml'));

% run openEMS simulation
RunOpenEMS(save_folder,'tmp.xml','');

disp('use Paraview to visualize the FDTD result...');
