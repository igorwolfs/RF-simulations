#######################################################################################
##################################### INTRO ###########################################
#######################################################################################

%{
%! INTRODUCTION
This example contains an excitation, created in order to measure the current and voltage at both start and end of the port.
This allows us to calculate the S-parameters.

%! MAIN TODO
A PEC is used here. The question however is why the fields are so limited to the PEC itself, and not spreading out more as they would normally do with a PEC.
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

physical_constants;
unit = 1e-6; % specify everything in um
MSL_length = 50000;
MSL_width = 600;
substrate_thickness = 254;
substrate_epr = 1;%3.66;
f_max = 7e9;


###############################################################################################
###################################### INITIALIZE FDTD ########################################
###############################################################################################

FDTD = InitFDTD();

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

CSX = InitCSX();
resolution = c0/(f_max*sqrt(substrate_epr))/unit /50; % resolution of lambda/50
mesh.x = SmoothMeshLines( [-MSL_length MSL_length], resolution, 1.5 ,0 );
mesh.y = SmoothMeshLines( [-15*MSL_width 15*MSL_width], resolution, 1.3 ,0);
mesh.z = SmoothMeshLines( [linspace(0,substrate_thickness,5) 10*substrate_thickness], resolution );
CSX = DefineRectGrid( CSX, unit, mesh );

%% substrate
CSX = AddMaterial( CSX, 'RO4350B' );
CSX = SetMaterialProperty( CSX, 'RO4350B', 'Epsilon', substrate_epr );
start = [mesh.x(1),   mesh.y(1),   0];
stop  = [mesh.x(end), mesh.y(end), substrate_thickness];
CSX = AddBox( CSX, 'RO4350B', 0, start, stop );

%% MSL port
CSX = AddMaterial( CSX, 'copper' );
CSX = SetMaterialProperty( CSX, 'copper', 'Kappa', 56e6 );

portstart = [ mesh.x(1), -MSL_width/2, substrate_thickness];
portstop  = [ 0,  MSL_width/2, 0];
display("MSL_port excite");
display(portstart);
display(portstop);

# Excitation vector [0, 0, -1]
[CSX,port{1}] = AddMSLPort( CSX, 999, 1, 'copper', portstart, portstop, 0, [0 0 -1], 'ExcitePort', true, 'FeedShift', 5*resolution, 'MeasPlaneShift',  MSL_length/3);
portstart = [mesh.x(end), -MSL_width/2, substrate_thickness];
portstop  = [0          ,  MSL_width/2, 0];

display("MSL_port normal");
display(portstart);
display(portstop);

# Excitation vector [0, 0, -1]
[CSX,port{2}] = AddMSLPort( CSX, 999, 2, 'copper', portstart, portstop, 0, [0 0 -1], 'MeasPlaneShift',  MSL_length/3 );

%% Filter-stub
start = [-MSL_width/2,  MSL_width/2, substrate_thickness];
stop  = [ MSL_width/2,  MSL_width/2, substrate_thickness];
CSX = AddBox( CSX, 'copper', 999, start, stop );
 

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