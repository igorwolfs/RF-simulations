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

% OpenEMS FDTD Analysis Automation Script
%
% To be run with GNU Octave or MATLAB.
% FreeCAD to OpenEMS plugin by Lubomir Jagos, 
% see https://github.com/LubomirJagos/FreeCAD-OpenEMS-Export
%
% This file has been automatically generated. Manual changes may be overwritten.
%

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
Sim_CSX = 'freecad_2_pads.xml';
[status, message, messageid] = rmdir( Sim_Path, 's' ); % clear previous directory
[status, message, messageid] = mkdir( Sim_Path ); % create empty simulation folder

%% setup FDTD parameter & excitation function
max_timesteps = 1000000;
min_decrement = 1e-05; % 10*log10(min_decrement) dB  (i.e. 1E-5 means -50 dB)
FDTD = InitFDTD( 'NrTS', max_timesteps, 'EndCriteria', min_decrement);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% BOUNDARY CONDITIONS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
BC = {"PEC","PEC","PEC","PEC","PEC","PEC"};
FDTD = SetBoundaryCond( FDTD, BC );

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% COORDINATE SYSTEM
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CSX = InitCSX('CoordSystem', 0); % Cartesian coordinate system.
mesh.x = []; % mesh variable initialization (Note: x y z implies type Cartesian).
mesh.y = [];
mesh.z = [];
CSX = DefineRectGrid(CSX, unit, mesh); % First call with empty mesh to set deltaUnit attribute.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MATERIALS AND GEOMETRY
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CSX = AddMetal( CSX, 'PEC' );

%% MATERIAL - PEC
CSX = AddMetal(CSX, 'PEC');
CSX = ImportSTL(CSX, 'PEC', 8400, [currDir '/board_wire#outline_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'PEC', 8500, [currDir '/board_area_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'PEC', 8600, [currDir '/board_solid_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});

%% MATERIAL - FR4
CSX = AddMaterial(CSX, 'FR4');
CSX = SetMaterialProperty(CSX, 'FR4', 'Epsilon', 4.0, 'Mue', 1.0, 'Kappa', 0.0, 'Sigma', 0.0);
CSX = ImportSTL(CSX, 'FR4', 8700, [currDir '/pads_wire#F.Cu#0#_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 8800, [currDir '/pads_area#F.Cu#0#_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 8900, [currDir '/pads_wire001#F.Cu#1#_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 9000, [currDir '/pads_area001#F.Cu#1#_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 9100, [currDir '/pads_area002#F.Cu_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 9200, [currDir '/track_wire#F.Cu#0.2_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 9300, [currDir '/track_area#F.Cu#0.2_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 9400, [currDir '/copper_area#F.Cu_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 9500, [currDir '/copper_solid#F.Cu_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 9600, [currDir '/zone_wire#B.Cu_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 9700, [currDir '/zone_area#B.Cu_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 9800, [currDir '/copper_area001#B.Cu_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 9900, [currDir '/copper_solid001#B.Cu_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});
CSX = ImportSTL(CSX, 'FR4', 10000, [currDir '/coppers_fuse#F.Cu_gen_model.stl'], 'Transform', {'Scale', fc_unit/unit});

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% GRID LINES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% GRID - 0.001 - board_wire#outline (Fixed Distance)
mesh.x(mesh.x >= 100 & mesh.x <= 105) = [];
mesh.x = [ mesh.x (100:0.001:105) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - board_area (Fixed Distance)
mesh.x(mesh.x >= 100 & mesh.x <= 105) = [];
mesh.x = [ mesh.x (100:0.001:105) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - board_solid (Fixed Distance)
mesh.x(mesh.x >= 100 & mesh.x <= 105) = [];
mesh.x = [ mesh.x (100:0.001:105) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 1.51) = [];
mesh.z = [ mesh.z (0:0.001:1.51) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - pads_wire#F.Cu#0# (Fixed Distance)
mesh.x(mesh.x >= -0.5 & mesh.x <= 0.5) = [];
mesh.x = [ mesh.x (-0.5:0.001:0.5) ];
mesh.y(mesh.y >= -0.5 & mesh.y <= 0.5) = [];
mesh.y = [ mesh.y (-0.5:0.001:0.5) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - pads_area#F.Cu#0# (Fixed Distance)
mesh.x(mesh.x >= 102 & mesh.x <= 103) = [];
mesh.x = [ mesh.x (102:0.001:103) ];
mesh.y(mesh.y >= -51 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-51:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - pads_wire001#F.Cu#1# (Fixed Distance)
mesh.x(mesh.x >= -0.5 & mesh.x <= 0.5) = [];
mesh.x = [ mesh.x (-0.5:0.001:0.5) ];
mesh.y(mesh.y >= -0.5 & mesh.y <= 0.5) = [];
mesh.y = [ mesh.y (-0.5:0.001:0.5) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - pads_area001#F.Cu#1# (Fixed Distance)
mesh.x(mesh.x >= 102 & mesh.x <= 103) = [];
mesh.x = [ mesh.x (102:0.001:103) ];
mesh.y(mesh.y >= -55 & mesh.y <= -54) = [];
mesh.y = [ mesh.y (-55:0.001:-54) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - pads_area002#F.Cu (Fixed Distance)
mesh.x(mesh.x >= 102 & mesh.x <= 103) = [];
mesh.x = [ mesh.x (102:0.001:103) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - track_wire#F.Cu#0.2 (Fixed Distance)
mesh.x(mesh.x >= 102.5 & mesh.x <= 102.5) = [];
mesh.x = [ mesh.x (102.5:0.001:102.5) ];
mesh.y(mesh.y >= -54.9 & mesh.y <= -50.1) = [];
mesh.y = [ mesh.y (-54.9:0.001:-50.1) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - track_area#F.Cu#0.2 (Fixed Distance)
mesh.x(mesh.x >= 102.4 & mesh.x <= 102.6) = [];
mesh.x = [ mesh.x (102.4:0.001:102.6) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - copper_area#F.Cu (Fixed Distance)
mesh.x(mesh.x >= 102 & mesh.x <= 103) = [];
mesh.x = [ mesh.x (102:0.001:103) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - copper_solid#F.Cu (Fixed Distance)
mesh.x(mesh.x >= 102 & mesh.x <= 103) = [];
mesh.x = [ mesh.x (102:0.001:103) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 1.51 & mesh.z <= 1.545) = [];
mesh.z = [ mesh.z (1.51:0.001:1.545) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - zone_wire#B.Cu (Fixed Distance)
mesh.x(mesh.x >= 100 & mesh.x <= 105) = [];
mesh.x = [ mesh.x (100:0.001:105) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
mesh.y = [ mesh.y (-55:0.001:-50) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - zone_area#B.Cu (Fixed Distance)
mesh.x(mesh.x >= 99.9825 & mesh.x <= 105.017) = [];
mesh.x = [ mesh.x (99.9825:0.001:105.017) ];
mesh.y(mesh.y >= -55.0175 & mesh.y <= -49.9825) = [];
mesh.y = [ mesh.y (-55.0175:0.001:-49.9825) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - copper_area001#B.Cu (Fixed Distance)
mesh.x(mesh.x >= 99.9825 & mesh.x <= 105.017) = [];
mesh.x = [ mesh.x (99.9825:0.001:105.017) ];
mesh.y(mesh.y >= -55.0175 & mesh.y <= -49.9825) = [];
mesh.y = [ mesh.y (-55.0175:0.001:-49.9825) ];
mesh.z(mesh.z >= 0 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (0:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - copper_solid001#B.Cu (Fixed Distance)
mesh.x(mesh.x >= 99.9825 & mesh.x <= 105.017) = [];
mesh.x = [ mesh.x (99.9825:0.001:105.017) ];
mesh.y(mesh.y >= -55.0175 & mesh.y <= -49.9825) = [];
mesh.y = [ mesh.y (-55.0175:0.001:-49.9825) ];
mesh.z(mesh.z >= -0.035 & mesh.z <= 0) = [];
mesh.z = [ mesh.z (-0.035:0.001:0) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%% GRID - 0.001 - coppers_fuse#F.Cu (Fixed Distance)
mesh.x(mesh.x >= 99.9825 & mesh.x <= 105.017) = [];
mesh.x = [ mesh.x (99.9825:0.001:105.017) ];
mesh.y(mesh.y >= -55.0175 & mesh.y <= -49.9825) = [];
mesh.y = [ mesh.y (-55.0175:0.001:-49.9825) ];
mesh.z(mesh.z >= -0.035 & mesh.z <= 1.545) = [];
mesh.z = [ mesh.z (-0.035:0.001:1.545) ];
CSX = DefineRectGrid(CSX, unit, mesh);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% RUN
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
WriteOpenEMS( [Sim_Path '/' Sim_CSX], FDTD, CSX );
CSXGeomPlot( [Sim_Path '/' Sim_CSX] );

if (postprocessing_only==0)
    %% run openEMS
    RunOpenEMS( Sim_Path, Sim_CSX, openEMS_opts );
end
