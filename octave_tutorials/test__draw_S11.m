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
physical_constants;
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
% EXCITATION 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
f0 = 1.5*1000000000.0;
fc = 0.4*1000000000.0;
max_res = c0 / (f0 + fc) / 20;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MATERIALS AND GEOMETRY
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CSX = AddMetal( CSX, 'PEC' );

%% MATERIAL - PEC
CSX = AddMetal(CSX, 'PEC');

%% MATERIAL - FR4
CSX = AddMaterial(CSX, 'FR4');
CSX = SetMaterialProperty(CSX, 'FR4', 'Epsilon', 4.0, 'Mue', 1.0, 'Kappa', 0.0, 'Sigma', 0.0);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PORTS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
portNamesAndNumbersList = containers.Map();

%% PORT -  - pads_area001#F.Cu#1#
portStart = [ 102, -55, 0 ];
portStop  = [ 103, -54, 0 ];
portR = 50.0;
portUnits = 1;
portExcitationAmplitude = 1.0;
mslDir = 1;
mslEVec = [0 0 -1]*portExcitationAmplitude;
[CSX port{1}] = AddMSLPort(CSX,10000,1,'PEC',portStart, portStop, mslDir, mslEVec, 'Feed_R', portR*portUnits);
portNamesAndNumbersList("pads_area001#F.Cu#1#") = 1;


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