% Plot S11
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
unit    = 0.001; % Model coordinates and lengths will be specified in mm.
fc_unit = 0.001; % STL files are exported in FreeCAD standard units (mm).

Sim_Path = 'simulation_output';
currDir = strrep(pwd(), '\', '\\');
display(currDir);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% COORDINATE SYSTEM
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CSX = InitCSX('CoordSystem', 0); % Cartesian coordinate system.
mesh.x = []; % mesh variable initialization (Note: x y z implies type Cartesian).
mesh.y = [];
mesh.z = [];
CSX = DefineRectGrid(CSX, unit, mesh); % First call with empty mesh to set deltaUnit attribute.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EXCITATION gps_sine
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
f0 = 1.5*1000000000.0;
fc = 0.2*1000000000.0;
max_res = c0 / (f0 + fc) / 20;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MATERIALS AND GEOMETRY
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CSX = AddMetal( CSX, 'PEC' );

%% MATERIAL - PEC
CSX = AddMetal(CSX, 'PEC');

%% MATERIAL - FR4
CSX = AddMaterial(CSX, 'FR4');
CSX = SetMaterialProperty(CSX, 'FR4', 'Epsilon', 4.0, 'Mue', 0.0, 'Kappa', 0.0, 'Sigma', 0.0);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% GRID LINES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% GRID - grid - board_wire#outline (Fixed Distance)
mesh.x(mesh.x >= 100 & mesh.x <= 105) = [];
mesh.x = [ mesh.x (100:0.001:105) ];
mesh.y(mesh.y >= -55 & mesh.y <= -50) = [];
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

%% PORT - microstrip_gps - coppers_fuse#F.Cu
portStart = [ 99.9825, -55.0175, 1.565 ];
portStop  = [ 105.017, -49.9825, -0.035 ];
portR = 50.0;
portUnits = 1;
portExcitationAmplitude = 1.0;
mslDir = 1;
mslEVec = [0 0 -1]*portExcitationAmplitude;
[CSX port{1}] = AddMSLPort(CSX,10000,1,'PEC',portStart, portStop, mslDir, mslEVec, 'Feed_R', portR*portUnits);
portNamesAndNumbersList("coppers_fuse#F.Cu") = 1;


%% postprocessing & do the plots
freq = linspace( max([0,f0-fc]), f0+fc, 501 );

port = calcPort(port, Sim_Path, freq);
s11 = port{1}.uf.ref ./ port{1}.uf.inc;
s11_dB = 20*log10(abs(s11));
Zin = port{1}.uf.tot ./ port{1}.if.tot;

% plot feed point impedance
figure
plotObj1 = plot( freq/1e6, real(Zin), 'k-', 'Linewidth', 2 );
hold on
grid on
plot( freq/1e6, imag(Zin), 'r--', 'Linewidth', 2 );
title( 'feed point impedance' );
xlabel( 'frequency f / MHz' );
ylabel( 'impedance Z_{in} / Ohm' );
legend( 'real', 'imag' );

figure
plotObj2 = plot( freq/1e6, 20*log10(abs(s11)), 'k-', 'Linewidth', 2 );
grid on
title( 'reflection coefficient S_{11}' );
xlabel( 'frequency f / MHz' );
ylabel( 'reflection coefficient |S_{11}|' );

% wait for plot windows to be closed
waitfor(plotObj1);
waitfor(plotObj2);

%
%   Write S11, real and imag Z_in into CSV file separated by ';'
%
filename = 'openEMS_simulation_s11_dB.csv';
fid = fopen(filename, 'w');
fprintf(fid, 'freq (MHz);s11 (dB);Z real (Ohm);Z imag (Ohm);Z abs (Ohm)\n');
fclose(fid)
s11_dB = horzcat((freq/1e6)', s11_dB', real(Zin)', imag(Zin)', abs(Zin)');
dlmwrite(filename, s11_dB, '-append', 'delimiter', ';');
