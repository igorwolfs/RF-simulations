% OpenEMS FDTD Analysis Automation Script
%
% To be run with GNU Octave or MATLAB.
% FreeCAD to OpenEMS plugin by Lubomir Jagos, 
% see https://github.com/LubomirJagos/FreeCAD-OpenEMS-Export
%
% This file has been automatically generated. Manual changes may be overwritten.
%

addpath('~/opt/openEMS/share/openEMS/matlab');
addpath('~/opt/openEMS/share/CSXCAD/matlab');
addpath('~/opt/openEMS/share/hyp2mat/matlab');

close all
clear
clc

%% Change the current folder to the folder of this m-file.
if(~isdeployed)
  mfile_name          = mfilename('fullpath');
  [pathstr,name,ext]  = fileparts(mfile_name);
  cd(pathstr);
end

%% constants
physical_constants;
unit    = 0.001; % Model coordinates and lengths will be specified in mm.
fc_unit = 0.001; % STL files are exported in FreeCAD standard units (mm).

%% switches & options
postprocessing_only = 0;
draw_3d_pattern = 0; % this may take a while...
use_pml = 0;         % use pml boundaries instead of mur

currDir = strrep(pwd(), '\', '\\');
display(currDir);

% --no-simulation : dry run to view geometry, validate settings, no FDTD computations
% --debug-PEC     : generated PEC skeleton (use ParaView to inspect)
openEMS_opts = '';

%% prepare simulation folder
Sim_Path = 'simulation_output';
Sim_CSX = 'waveguide.xml';
[status, message, messageid] = rmdir( Sim_Path, 's' ); % clear previous directory
[status, message, messageid] = mkdir( Sim_Path ); % create empty simulation folder

%% setup FDTD parameter & excitation function
max_timesteps = 1000000;
min_decrement = 1e-05; % 10*log10(min_decrement) dB  (i.e. 1E-5 means -50 dB)
FDTD = InitFDTD( 'NrTS', max_timesteps, 'EndCriteria', min_decrement);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% BOUNDARY CONDITIONS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
BC = {"PML_8","PML_8","PML_8","PML_8","PML_8","PML_8"};
FDTD = SetBoundaryCond( FDTD, BC );

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% COORDINATE SYSTEM
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CSX = InitCSX('CoordSystem', 0); % Cartesian coordinate system.
mesh.x = []; % mesh variable initialization (Note: x y z implies type Cartesian).
mesh.y = [];
mesh.z = [];
% deltaunit: unit 1 um, mesh: 
CSX = DefineRectGrid(CSX, unit, mesh); % First call with empty mesh to set deltaUnit attribute.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EXCITATION gps_sine
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
f0 = 1.5*1000000000.0;
fc = 0.2*1000000000.0;
FDTD = SetGaussExcite( FDTD, f0, fc );
max_res = c0 / (f0 + fc) / 20;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MATERIALS AND GEOMETRY
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% MATERIAL - PEC
CSX = AddMetal(CSX, 'PEC');
CSX = ImportSTL(CSX, 'PEC', 9100, [currDir './copper_plane.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'PEC', 9200, [currDir '/copper_trace.stl'], 'Transform', {'Scale', fc_unit/unit});

%% MATERIAL - FR4
CSX = AddMaterial(CSX, 'FR4');
CSX = SetMaterialProperty(CSX, 'FR4', 'Epsilon', 4.0, 'Mue', 1.0, 'Kappa', 0.0, 'Sigma', 0.0);
CSX = ImportSTL(CSX, 'FR4', 9000, [currDir '/board_dielectric.stl'], 'Transform', {'Scale', fc_unit/unit});

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% GRID LINES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% GRID - grid - board_wire#outline (Fixed Distance)
mesh.x(mesh.x >= 100 & mesh.x <= 105) = [];

% Array from 100 to 105, with increments of 0.001
mesh.x = [ mesh.x (100:0.001:105) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
% Array from -55 to -50, with decrements of -0.001
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - grid - board_solid (Fixed Distance)
mesh.x(mesh.x >= 100 & mesh.x <= 105) = [];
mesh.x = [ mesh.x (100:0.001:105) ];

mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 1.53) = [];
mesh.z = [ mesh.z (0:0.001:1.53) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - grid - track_wire#F.Cu#0.2 (Fixed Distance)
mesh.x(mesh.x >= 102.5 & mesh.x <= 102.5) = [];
mesh.x = [ mesh.x (102.5:0.001:102.5) ];
mesh.y(mesh.y >= -54.9 & mesh.y <= -50.1) = [];
mesh.y = [ mesh.y (-54.9:0.001:-50.1) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - grid - track_area#F.Cu#0.2 (Fixed Distance)
mesh.x(mesh.x >= 102.4 & mesh.x <= 102.6) = [];
mesh.x = [ mesh.x (102.4:0.001:102.6) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - grid - copper_area#F.Cu (Fixed Distance)
mesh.x(mesh.x >= 102.4 & mesh.x <= 102.6) = [];
mesh.x = [ mesh.x (102.4:0.001:102.6) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - grid - copper_solid#F.Cu (Fixed Distance)
mesh.x(mesh.x >= 102.4 & mesh.x <= 102.6) = [];
mesh.x = [ mesh.x (102.4:0.001:102.6) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 1.53 & mesh.z <= 1.565) = [];
mesh.z = [ mesh.z (1.53:0.001:1.565) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - grid - board_area (Fixed Distance)
mesh.x(mesh.x >= 100 & mesh.x <= 105) = [];
mesh.x = [ mesh.x (100:0.001:105) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - grid - zone_wire#B.Cu (Fixed Distance)
mesh.x(mesh.x >= 100 & mesh.x <= 105) = [];
mesh.x = [ mesh.x (100:0.001:105) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - grid - zone_area#B.Cu (Fixed Distance)
mesh.x(mesh.x >= 99.9825 & mesh.x <= 105.017) = [];
mesh.x = [ mesh.x (99.9825:0.001:105.017) ];
mesh.y(mesh.y >= -55.0175 & mesh.y <= -49.9825) = [];
mesh.y = [ mesh.y (-55.0175:0.001:-49.9825) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - grid - copper_area001#B.Cu (Fixed Distance)
mesh.x(mesh.x >= 99.9825 & mesh.x <= 105.017) = [];
mesh.x = [ mesh.x (99.9825:0.001:105.017) ];
mesh.y(mesh.y >= -55.0175 & mesh.y <= -49.9825) = [];
mesh.y = [ mesh.y (-55.0175:0.001:-49.9825) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - grid - copper_solid001#B.Cu (Fixed Distance)
mesh.x(mesh.x >= 99.9825 & mesh.x <= 105.017) = [];
mesh.x = [ mesh.x (99.9825:0.001:105.017) ];
mesh.y(mesh.y >= -55.0175 & mesh.y <= -49.9825) = [];
mesh.y = [ mesh.y (-55.0175:0.001:-49.9825) ];
mesh.z(mesh.z >= -0.035 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (-0.035:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - grid - coppers_fuse#F.Cu (Fixed Distance)
mesh.x(mesh.x >= 99.9825 & mesh.x <= 105.017) = [];
mesh.x = [ mesh.x (99.9825:0.001:105.017) ];
mesh.y(mesh.y >= -55.0175 & mesh.y <= -49.9825) = [];
mesh.y = [ mesh.y (-55.0175:0.001:-49.9825) ];
mesh.z(mesh.z >= -0.035 & mesh.z <= 1.565) = [];
mesh.z = [ mesh.z (-0.035:0.001:1.565) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PORTS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
portNamesAndNumbersList = containers.Map();

% portStart -> portStop: [0,     -width/2,   height]
% portStop -> portStop: [length   width/2   0]
portStart = [ 99.9, -55, 1.565 ];
portStop  = [ 105.02, -50.00, -0.035 ];
portR = 50.0;
portUnits = 1;
portExcitationAmplitude = 1.0;
mslDir = 1;
mslEVec = [0 0 -1]*portExcitationAmplitude;

% CSX = AddBox( CSX, materialname, prio, MSL_start, MSL_stop );
% ISSUE: for some reason it adds the full thing to it.
% portstart and portstop are simply huge -> you need some kind-of component there where you start the excitation from.

[CSX port{1}] = AddMSLPort(CSX,10000,1,'PEC',portStart, portStop, mslDir, mslEVec, 'Feed_R', portR*portUnits);
portNamesAndNumbersList("coppers_fuse#F.Cu") = 1;

