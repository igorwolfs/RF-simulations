#######################################################################################
##################################### INTRO ###########################################
#######################################################################################

%{
%! INTRODUCTION
This example contains an excitation, created in order to measure the current and voltage at both start and end of the port.
This allows us to calculate the S-parameters.

%! MAIN TODO
Make a mix between this one and the MSL_pec, 
so we can actually calculate the total end impedance and the S-parameters.

-> WEIRD: for some reason the ports must always be 2d, no idea why they can't have a height.
This is probably to allow a distributed excitation. (excitation goes from exc_start to exc_stop)
HOWEVER: start, stop here in the propagation direction are at the same index.

MAYBE I MISSED THE WHOLE POINT, MAYBE THE EXCITATION IS ALWAAYS IN THE XY PLANE AND NOT IN THE Z PLANE? https://github.com/thliebig/openEMS-Project/discussions/162
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
MSL_xmin = -50000;
MSL_xmax = 50000;
MSL_ymin = -600;
MSL_ymax = 600;
substrate_thickness = 508;
substrate_epr = 1; % 3.66;
f_max = 7e9;

###############################################################################################
###################################### INITIALIZE FDTD ########################################
###############################################################################################

max_timesteps = 20000;
FDTD = InitFDTD(max_timesteps);

#############################################################################################
################################# BOUNDARY CONDITIONS #######################################
#############################################################################################

BC   = {'PML_8' 'PML_8' 'MUR' 'MUR' 'PEC' 'MUR'};
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
resolution = c0/(f_max*sqrt(substrate_epr))/unit /50; % resolution of lambda/50
mesh.x = SmoothMeshLines( [MSL_xmin MSL_xmax], resolution, 1.5 ,0 );
mesh.y = SmoothMeshLines( [15*MSL_ymin 15*MSL_ymax], resolution, 1.3 ,0);

%% linspace: divides substrate_thickness into 5 steps (0 -> 5)
mesh.z = SmoothMeshLines( [linspace(0, substrate_thickness, 11) 10*substrate_thickness], resolution );
CSX = DefineRectGrid( CSX, unit, mesh );
display(mesh.z)

%% substrate
CSX = AddMaterial( CSX, 'RO4350B' );
CSX = SetMaterialProperty( CSX, 'RO4350B', 'Epsilon', substrate_epr );
start = [mesh.x(1),   mesh.y(1),   0];
stop  = [mesh.x(end), mesh.y(end), substrate_thickness];
CSX = AddBox( CSX, 'RO4350B', 0, start, stop );

%% MSL port
CSX = AddMetal( CSX, 'PEC' );

port1start = [mesh.x(1), 2*MSL_ymin, (1/2) * substrate_thickness/2];
port1stop  = [mesh.x(1) + resolution*20,  2*MSL_ymax, (3/2) * substrate_thickness];
port2start = [mesh.x(end), 2*MSL_ymin, (1/2) * substrate_thickness/2];
port2stop  = [mesh.x(end) - resolution*20,  2*MSL_ymax, (3/2) * substrate_thickness];

display("port1 start stop");
display(port1start);
display(port1stop);
display("port1 start stop");
display(port2start);
display(port2stop);


conductorbox_start = [mesh.x(1), MSL_ymin, substrate_thickness/2];
conductorbox_end = [mesh.x(end), MSL_ymax, substrate_thickness];

priority = 100
CSX = AddBox( CSX, 'PEC', priority, conductorbox_start, conductorbox_end );

# Excitation vector [0, 0, -1]
%! The measure plane shift is always larger than the excitation plane shift (obviously) since it would otherwise lead to erroneous measurements.
[CSX,port{1}] = AddMSLPort( CSX, 999, 1, 'PEC', port1start, port1stop, 0, [0 0 -1], 'ExcitePort', true, 'FeedShift', 10*resolution, 'MeasPlaneShift',  15*resolution);

# Excitation vector [0, 0, -1]
[CSX,port{2}] = AddMSLPort( CSX, 999, 2, 'PEC', port2start, port2stop, 0, [0 0 -1], 'MeasPlaneShift',  10*resolution );

####################################################################################
#################################### DUMPS #########################################
####################################################################################

start = [mesh.x(1) mesh.y(1) mesh.z(1)];
stop = [mesh.x(end) mesh.y(end) mesh.z(end)];

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
RunOpenEMS( mfilename, Sim_CSX );

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
%? WHY IS THE THICKNESS ACTUALLY PASSED? Where is it in fact used?
The actual excitation box is equal to 0 in the propagation direction, and (port width, port height) in the other directions.
So the excitation "box" has the height and width dimensions passed in cross-sectional plane of the conductor.
%? Does this entire plane actually get excited?
-> Check in engine code how this happens

Excitations here are put
*voltage* dir: 2 0 <<< (5,11,0), [Coords: (-45726.50,0.00,31.75)], [prop:0x60325709a3d0, elec:0x60325709a3d0, GetActiveDir:true, ExciteType:0][amp:-0.000, GetWeightedExcitation:-1.000, GetEdgeLength:0.000], amp, >>>
*voltage* dir: 2 0 <<< (5,11,1), [Coords: (-45726.50,0.00,95.25)], [prop:0x60325709a3d0, elec:0x60325709a3d0, GetActiveDir:true, ExciteType:0][amp:-0.000, GetWeightedExcitation:-1.000, GetEdgeLength:0.000], amp, >>>
*voltage* dir: 2 0 <<< (5,11,2), [Coords: (-45726.50,0.00,158.75)], [prop:0x60325709a3d0, elec:0x60325709a3d0, GetActiveDir:true, ExciteType:0][amp:-0.000, GetWeightedExcitation:-1.000, GetEdgeLength:0.000], amp, >>>
*voltage* dir: 2 0 <<< (5,11,3), [Coords: (-45726.50,0.00,222.25)], [prop:0x60325709a3d0, elec:0x60325709a3d0, GetActiveDir:true, ExciteType:0][amp:-0.000, GetWeightedExcitation:-1.000, GetEdgeLength:0.000], amp, >>>

So the voltage that excites does in fact excite along the entire z-axis. The excitation plane is across the entire z-axis.
The main question becomes: how does the excitation look like?
-> This probably needs to be checked out elsewhere, since the excitation type itself together with frequency was defined in the FDTD simulation.
Now: actually go into the engine and check how that's done.
%}