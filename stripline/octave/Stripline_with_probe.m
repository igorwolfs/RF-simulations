#############################################################################################
##################################### PATHS ADDED ###########################################
#############################################################################################

addpath('~/opt/openEMS/share/openEMS/matlab');
addpath('~/opt/openEMS/share/CSXCAD/matlab');
addpath('~/opt/openEMS/share/hyp2mat/matlab');

close all
clear
clc

save_folder = 'Stripline';
probe = true;

###############################################################################################
###################################### SET CONSTANTS ###########################################
###############################################################################################

physical_constants;
unit = 1e-6; % specify everything in um
SL_length = 50000;
SL_width = 520;
SL_height = 500;
substrate_thickness = SL_height;
substrate_epr = 3.66;
f_max = 7e9;

###############################################################################################
###################################### INITIALIZE FDTD ########################################
###############################################################################################

%% setup FDTD parameters & excitation function %%%%%%%%%%%%%%%%%%%%%%%%%%%%
FDTD = InitFDTD();

#############################################################################################
################################# BOUNDARY CONDITIONS #######################################
#############################################################################################

BC   = {'PML_8' 'PML_8' 'PMC' 'PMC' 'PEC' 'PEC'};
FDTD = SetBoundaryCond( FDTD, BC );

#####################################################################################
################################# GRID / MESH #######################################
#####################################################################################

%% setup CSXCAD geometry & mesh %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CSX = InitCSX();
resolution = c0/(f_max*sqrt(substrate_epr)) / unit / 50; % resolution of lambda/50
mesh.x = SmoothMeshLines( [-SL_length/2 0 SL_length/2], resolution, 1.5 ,0 );
mesh.y = SmoothMeshLines( [0 SL_width/2+[-resolution/3 +resolution/3*2]/4], resolution/4 , 1.5 ,0);
mesh.y = SmoothMeshLines( [-10*SL_width -mesh.y mesh.y 10*SL_width], resolution, 1.3 ,0);
height_variation = 0;
mesh.z = linspace(0,substrate_thickness+height_variation, 11);
mesh.z = sort(unique([mesh.z -mesh.z]));
CSX = DefineRectGrid( CSX, unit, mesh );

####################################################################################
################################# EXCITATION #######################################
####################################################################################

FDTD = SetGaussExcite( FDTD, f_max/2, f_max/2 );

%% substrate
% x: SL_length, y: SL_width, z: SL_height
CSX = AddMaterial( CSX, 'RO4350B' );
CSX = SetMaterialProperty( CSX, 'RO4350B', 'Epsilon', substrate_epr );
start = [mesh.x(1),   mesh.y(1),   mesh.z(1)];
stop  = [mesh.x(end), mesh.y(end), mesh.z(end)];
CSX = AddBox( CSX, 'RO4350B', 0, start, stop );

%% SL port 
% Z = 0, infinitely thin inside xy plane (width: y = SL_width, length: SL_length)
CSX = AddMetal( CSX, 'PEC' );
portstart = [ mesh.x(1), -SL_width/2, 0];
portstop  = [ 0,         SL_width/2, 0];
[CSX,port{1}] = AddStripLinePort( CSX, 999, 1, 'PEC', portstart, portstop, SL_height, 'x', [0 0 -1], 'ExcitePort', true, 'FeedShift', 10*resolution, 'MeasPlaneShift',  SL_length/3);

portstart = [mesh.x(end), -SL_width/2, 0];
portstop  = [0          ,  SL_width/2, 0];
[CSX,port{2}] = AddStripLinePort( CSX, 999, 2, 'PEC', portstart, portstop, SL_height, 'x', [0 0 -1], 'MeasPlaneShift',  SL_length/3 );

%{
%! Creation of SL port
% * Thickness
- The stripline is created at z=start(3) so at point 0.
- The thickness of the stripline is 0.

% * Measuring


% * Excitation
The excitation is created at z=excitation start / stop +- height_vector (start = stop)
So for excitation = 0 -> your excitation happens at +height and -height. 
The substrate thickness goes from -500 to 500 um.
-> there are PEC's o z1 and z2, which is what a stripline is supposed to have.
%}

####################################################################################
#################################### DUMPS #########################################
#########################3###########################################################

%{
TIME DOMAIN FOR FIELD DUMP BOX
%! Choosing different heights
For some reason, when choosing a height of [-500, 500] the excitation doesn't show on the top layer.
- Same for when we choose [-450, 500].
- When choosing [-500, 450] The excitation appears on both sides.
When changing the simulation grid to -600 -> 600
- height_variation = 100;
- mesh.z = linspace(0,substrate_thickness+height_variation, 13)
The same happens! SO: the bottom shows a magnitude electric field, the top doesn't for some reason.
All while normally it shouldn't show an electric field, since the 
When we then display [-500, 500] for this situation it actually does work.
SO: probably what happens is 2-fold
1. The upper part of the grid did not get simulated for some reason.
2. Paraview only displays the top / bottom z-layer OR this information is not stored
    -> Note: this is easily checkable by loading the data from a .vtr file.
% NOTE: you can't just increase the simulation size and ignore the dielectric, because then you ignore the PEC boundary condition required for a TEM-waveform in the stripline case.
%}
start = [mesh.x(1) mesh.y(1) -450];
stop = [mesh.x(end) mesh.y(end) 450];

CSX = AddDump(CSX,'Et','DumpMode',0);
CSX = AddBox(CSX,'Et',0, start, stop);

%{
% !DISPLAYING THE DUMP
When displaying the 3D file, we only see one layer of fields in the Z-direction.
HOWEVER: Multiple fields exist in different z-layers, this was tested by changing the z-range and seeing different fields on display.
%}

####################################################################################
#################################### SIM-RUN #######################################
####################################################################################

%% write/show/run the openEMS compatible xml-file
Sim_Path = ['tmp_' mfilename];
Sim_CSX = 'stripline.xml';

[status, message, messageid] = rmdir( Sim_Path, 's' ); % clear previous directory
[status, message, messageid] = mkdir( Sim_Path ); % create empty simulation folder

WriteOpenEMS( [Sim_Path '/' Sim_CSX], FDTD, CSX );
CSXGeomPlot( [Sim_Path '/' Sim_CSX] );
RunOpenEMS( Sim_Path, Sim_CSX );


#######################################################################################
#################################### PLOTTING #########################################
#######################################################################################

%% post-processing
close all
f = linspace( 1e6, f_max, 1601 );
port = calcPort( port, Sim_Path, f, 'RefImpedance', 50);

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
title ("erf (x) with text annotation");
ylim([-50 2]);
pdf_filepath = strcat("tmp_", mfilename, "/", mfilename, ".pdf");
print (hf, pdf_filepath, "-dpdf");

display("dump: ");
display(start);
display(stop);


#######################################################################################
#################################### COMMENTS #########################################
#######################################################################################

%{

% TODO:
unset GTK_PATH
%}
