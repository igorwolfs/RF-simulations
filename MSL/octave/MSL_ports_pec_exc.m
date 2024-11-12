#######################################################################################
##################################### INTRO ###########################################
#######################################################################################

%{
%! INTRODUCTION
This example contains an excitation, created in order to measure the current and voltage at both start and end of the port.
This allows us to calculate the S-parameters.

%! MAIN TODO
We want to create a simulation where the.
- Conductor is on the top, next to the dielectric.
- Dielectric is all the way below.
- The excitation on top and bottom of the dielectric


typical substrate thickness: 1600 um
typical copper thickness: 36 um
typical trace width: 500 um

%}


#############################################################################################
##################################### PATHS ADDED ###########################################
#############################################################################################


addpath('~/opt/openEMS/share/openEMS/matlab');
addpath('~/opt/openEMS/share/CSXCAD/matlab');
addpath('~/opt/openEMS/share/hyp2mat/matlab');


close all
clear
clc

###############################################################################################
###################################### SET CONSTANTS ###########################################
###############################################################################################
% DISABLED: shows simply propagating wave

physical_constants;
unit = 1e-6; % specify everything in um
MSL_dz = 36;  % thickness
MSL_dy = 500;  % trace width
MSL_dx = 200e3  % 500 mm

%{
port1_dx = 50e3;
port1_exc_dx = 20e3;
port1_meas_dx = 30e3;
port2_dx = 50e3;10e3
port2_meas_dx = 30e3;
%}

port1_dx = 10e3;
port1_exc_dx = 5e3;
port1_meas_dx = 8e3;
port2_dx = 10e3;
port2_meas_dx = 5e3;

substrate_thickness = 1.6e3; % 1.6 mm
substrate_epr = 3.66;
f_max = 7e9;
% Wavelength
wavelength = c0/(f_max*sqrt(substrate_epr));
wavelength_u = wavelength / unit;

###############################################################################################
###################################### INITIALIZE FDTD ########################################
###############################################################################################

max_timesteps = 900000;

FDTD = InitFDTD(max_timesteps);

#############################################################################################
################################# BOUNDARY CONDITIONS #######################################
#############################################################################################


# CLOSE OFF TOP WITH MUR (AIR) BOTTOM WITH PEC (MSL)
SIM_BOX = [-MSL_dx/2, MSL_dx/2, -MSL_dy*5, MSL_dy*5, -substrate_thickness, 0];
display("---- SIM_BOX ----");
display(SIM_BOX)
display("---- SIM_BOX ----");

BC   = {'PML_8' 'PML_8' 'PML_8' 'PML_8' 'PEC' 'PML_8'};
FDTD = SetBoundaryCond( FDTD, BC );

####################################################################################
################################# EXCITATION #######################################
####################################################################################

FDTD = SetGaussExcite( FDTD, f_max/2, f_max/2 );

#####################################################################################
################################# GRID / MESH #######################################
#####################################################################################

%{
% !TODO:
- Increase the substrate thickness to 2 times the size
- Choose the PEC the thickness of the substrate
- Put the PEC on top of the substrate with the relevant thickness
%}

CSX = InitCSX();


%% linspace(start, stop, n_steps): divides "start", "stop" into "n_steps" steps

% Resolution, max_resolution, Ratio
mesh.x = [SIM_BOX(1) SIM_BOX(2)];
mesh.y = [SIM_BOX(3) SIM_BOX(4)];
mesh.z = [SIM_BOX(5) SIM_BOX(6)];



%%%%%%% substrate %%%%%%%%%
%! GOAL: put the grid in place for the dielectric (resolution: wavelength / 20)
% Resolution
display("---- SUBSTRATE ----");

resolution_x = wavelength / 20;
resolution_u_x = resolution_x / unit;
resolution_y = wavelength / 30;
resolution_u_y = resolution_y / unit;
resolution_z = wavelength / 20;
resolution_u_z = resolution_z / unit;

printf("Resolution: %.2f, %.2f, %.2f\r\n", resolution_x, resolution_y, resolution_z);
printf("Resolution: %.2f, %.2f, %.2f\r\n", resolution_u_x, resolution_u_y, resolution_u_z);
mesh.x = [SmoothMeshLines([SIM_BOX(1) SIM_BOX(2)], resolution_u_x ) mesh.x]
mesh.y = [SmoothMeshLines([SIM_BOX(3) SIM_BOX(4)], resolution_u_y ) mesh.y]
mesh.z = [SmoothMeshLines([SIM_BOX(5) SIM_BOX(6)], resolution_u_z ) mesh.z]

CSX = AddMaterial( CSX, 'RO4350B' );


CSX = SetMaterialProperty( CSX, 'RO4350B', 'Epsilon', substrate_epr);
start = [SIM_BOX(1), SIM_BOX(3), SIM_BOX(5)];
stop  = [SIM_BOX(2), SIM_BOX(4), SIM_BOX(6)];
CSX = AddBox( CSX, 'RO4350B', 0, start, stop );
display("---- SUBSTRATE ----");

%%%%%%% CONDUCTOR %%%%%%%%%
display("---- CONDUCTOR ----");

CSX = AddMetal( CSX, 'PEC' );

priority = 100;
conductorbox_start =  [-MSL_dx/2, -MSL_dy/2, -MSL_dz];
conductorbox_end    = [ MSL_dx/2,  MSL_dy/2,  0];
CSX = AddBox( CSX, 'PEC', priority, conductorbox_start, conductorbox_end );
% mesh.z = [linspace(conductorbox_start(3), conductorbox_end(3), 6) mesh.z];

%%%%%%% PORTS %%%%%%%%%
# ACTUALLY DEFINE MESH HERE
%%%%%%% PORT 1 EXC

display("---- PORT1 EXC ----");


% Excite "pec-width" above the conductor
port1start = [-MSL_dx/2,          -MSL_dy/2,  0];
port1stop  = [-MSL_dx/2+port1_dx,  MSL_dy/2,  MSL_dz];



mesh.x = [linspace(port1start(1)+port1_exc_dx-300, port1start(1)+port1_exc_dx+300, 11) mesh.x];
mesh.x = [linspace(port1start(1)+port1_meas_dx-300, port1start(1)+port1_meas_dx+300, 11) mesh.x];

mesh.y = [linspace(port1start(2)*(3/2), port1stop(2)*(3/2), 6) mesh.y];
mesh.z = [linspace(port1start(3)*(3/2), port1stop(3)*(3/2), 6) mesh.z];

display("Adding grids for port:");

display("added y: ");
display(linspace(port1start(2)*(3/2), port1stop(2)*(3/2), 11));

display("added z: ");
display(linspace(port1start(3)*(3/2), port1stop(3)*(3/2), 6));

display("port1 start stop");
display(port1start);
display(port1stop);
display("---- PORT1 EXC ----");

%%%%%%% PORT 2 EXC
display("---- PORT2 ----");

port2start = [(MSL_dx/2),          -MSL_dy/2, 0];
port2stop  = [(MSL_dx/2)-port2_dx,  MSL_dy/2,  MSL_dz];

mesh.x = [linspace(port2start(1)-port2_meas_dx-300, port2start(1)-port2_meas_dx+300, 21) mesh.x];

display("port2 start stop");
display(port2start);
display(port2stop);

display("---- PORT2 ----");

CSX = DefineRectGrid( CSX, unit, mesh );


# Excitation vector [0, 0, 1]
%! The measure plane shift is always larger than the excitation plane shift (obviously) since it would otherwise lead to erroneous measurements.
[CSX,port{1}] = AddMSLPort( CSX, 999, 1, 'PEC', port1start, port1stop, 0, [0 0 1], 'ExcitePort', true, 'FeedShift', port1_exc_dx, 'MeasPlaneShift',  port1_meas_dx);

# Excitation vector [0, 0, -1]
[CSX,port{2}] = AddMSLPort( CSX, 999, 2, 'PEC', port2start, port2stop, 0, [0 0 -1], 'MeasPlaneShift',  port2_meas_dx );

####################################################################################
#################################### DUMPS #########################################
####################################################################################

start = [SIM_BOX(1), SIM_BOX(3), SIM_BOX(5)];
stop  = [SIM_BOX(2), SIM_BOX(4), SIM_BOX(6)];

CSX = AddDump(CSX,'Et','DumpMode',0);
CSX = AddBox(CSX,'Et',0, start, stop);

####################################################################################
#################################### SIM-RUN #######################################
####################################################################################


Sim_CSX = strcat([mfilename '.xml']);

[status, message, messageid] = rmdir( mfilename, 's' ); % clear previous directory
[status, message, messageid] = mkdir( mfilename ); % create empty simulation folder

WriteOpenEMS( [mfilename '/' Sim_CSX], FDTD, CSX );
CSXGeomPlot( [mfilename '/' Sim_CSX] );
RunOpenEMS( mfilename, Sim_CSX, '--debug-material', true, '--debug-PEC', true, '--debug-operator', true, '--debug-boxes', true, '--debug-CSX', true);

#######################################################################################
#################################### PLOTTING #########################################
#######################################################################################

%% post-processing
close all
f = linspace( 1e6, f_max, 1601 );
port = calcPort( port, mfilename, f, 'RefImpedance', 50);

s11 = port{1}.uf.ref./ port{1}.uf.inc;
s21 = port{2}.uf.ref./ port{1}.uf.inc;

hf = figure()
plot(f/1e9,20*log10(abs(s11)),'k-','LineWidth',2);
hold on;
grid on;
plot(f/1e9,20*log10(abs(s21)),'r--','LineWidth',2);
legend('S_{11}','S_{21}');
ylabel('S-Parameter (dB)','FontSize',12);
xlabel('frequency (GHz) \rightarrow','FontSize',12);
ylim([-40 2]);
pdf_filepath = strcat(mfilename, "/", mfilename, ".pdf");

print (hf, pdf_filepath, "-dpdf");


#######################################################################################
#################################### COMMENTS #########################################
#######################################################################################
%{
%! GRID CREATION
Make sure that the grid around the excitation source is small enough, so the excitation propagates well.
Also make sure the excitation mesh there is equidistant 

%! QUCS SIMULATOR RF OPENEMS PLUGIN
https://github.com/thomaslepoix/Qucs-RFlayout/blob/master/doc/tutorials/openems.md
Gives tips on how meshes are generated with QUCS
These filters can then also be turned into kicad footprints
%}


%{
The power keeps going up here until it reaches infinity. 
-> The main reason seemed to be the closeness to the 
%}