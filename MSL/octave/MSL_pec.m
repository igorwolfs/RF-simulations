#############################################################################################
##################################### PATHS ADDED ###########################################
#############################################################################################


addpath('~/opt/openEMS/share/openEMS/matlab');
addpath('~/opt/openEMS/share/CSXCAD/matlab');
addpath('~/opt/openEMS/share/hyp2mat/matlab');


close all
clear
clc

%% prepare simulation folder

Sim_CSX = strcat([mfilename 'xml'])
[status, message, messageid] = rmdir( mfilename, 's' ); % clear previous directory
[status, message, messageid] = mkdir( mfilename ); % create empty simulation folder


###############################################################################################
###################################### SET CONSTANTS ###########################################
###############################################################################################

%% setup the simulation
physical_constants;
unit = 1e-3; % all length in mm


###############################################################################################
###################################### INITIALIZE FDTD ########################################
###############################################################################################

max_timesteps = 3000;
min_decrement = 1e-5; % equivalent to -50 dB

FDTD = InitFDTD( max_timesteps, min_decrement );

#############################################################################################
################################# BOUNDARY CONDITIONS #######################################
#############################################################################################

# Y1, Z1, Z2 are PEC layers. Why?
# NOTE: Z1 and Z2 are the propagation directions
% BC = {'PMC' 'PMC' 'PEC' 'PMC' 'PEC' 'PEC'};

%{
% !NOTE: When putting a PML_8 condition at the point of excitation (y=0), it simply absorbs the excitation wave before it even manages to propagate!
%}
BC = {'PML_8' 'PML_8' 'PEC' 'PML_8' 'PEC' 'PEC'};
FDTD = SetBoundaryCond( FDTD, BC );


####################################################################################
################################# EXCITATION #######################################
####################################################################################

f0 = 2e9; % center frequency
fc = 1e9; % 10 dB corner frequency (in this case 1e9 Hz - 3e9 Hz)
FDTD = SetGaussExcite( FDTD, f0, fc );

#####################################################################################
################################# GRID / MESH #######################################
#####################################################################################

%% setup CSXCAD geometry & mesh

% geometry
length = 600;
width = 400;
height = 200;
MSL_width = 50;
MSL_height = 10;

% very simple mesh
CSX = InitCSX();
resolution = c0/(f0+fc)/unit / 15; % resolution of lambda/15
mesh.x = SmoothMeshLines( [-width/2, width/2, -MSL_width/2, MSL_width/2], resolution ); % create smooth lines from fixed lines
% !NOTE: it seems like the MSL height is only 1 unit inside the simulation
mesh.y = SmoothMeshLines( [linspace(0,MSL_height,5) MSL_height+1 height], resolution );
mesh.z = SmoothMeshLines( [0 length], resolution );
CSX = DefineRectGrid( CSX, unit, mesh );


%% create MSL
% attention! the skin effect is not simulated, because the MSL is discretized with only one cell!
%{
% ! USING A PEC
When using a PEC here as waveguide, the conductivity is infinite.
Because of this, there is no current running through the inductor, the electric field is 0 on the surface and inside of it.
AND the fields stay outside of the conductor itself.
% ! USING A NON-IDEAL CONDUCTOR
A non-ideal conductor has an electric field inside the conductor which in turn produces a current which produces a magnetic field.
The equations governing the magnetic and electric fields in and around the conductor say that there is an exponential decay of the fields to the inside of the conductor due to the skin effect.
Because of this the electric fields are restricted to the surface region of the conductor, which is indeed what we see in a non-ideal conductor.
%}
CSX = AddMaterial( CSX, 'PEC' );

%{
Height: (y-dir): 1e-3
Width:  (x-dir): MSL_width:  50 mm
Length: (z-dir): 600 mm
%}

start = [-MSL_width/2, MSL_height,   0];
stop  = [ MSL_width/2, MSL_height+1, length];
priority = 100; % the geometric priority is set to 100
CSX = AddBox( CSX, 'PEC', priority, start, stop );

%% add excitation below the strip
start = [-MSL_width/2, 0         , mesh.z(1)];
stop  = [ MSL_width/2, MSL_height, mesh.z(1)];
CSX = AddExcitation( CSX, 'excite', 0, [0 -1 0] );
CSX = AddBox( CSX, 'excite', 0, start, stop );

epsilon = 4.0;
CSX = AddMaterial( CSX, 'FR4' );
CSX = SetMaterialProperty( CSX, 'FR4', 'Epsilon', epsilon);
%% Add dielectric below the strip -> Check the influence on the characteristic impedance
start = [-width/2, 0          , mesh.z(1)];
stop =  [ width/2, MSL_height , mesh.z(end)];
CSX = AddBox( CSX, 'FR4', 0, start, stop );

####################################################################################
#################################### DUMPS #########################################
####################################################################################

%% define dump boxes
start = [mesh.x(1),  MSL_height/2, mesh.z(1)];
stop  = [mesh.x(end), MSL_height/2, mesh.z(end)];
CSX = AddDump( CSX, 'Et_', 'DumpMode', 2 ); % cell interpolated
CSX = AddBox( CSX, 'Et_', 0, start, stop );

%% define voltage calc box
% voltage calc boxes will automatically snap to the next mesh-line
CSX = AddProbe( CSX, 'ut1', 0 );
zidx  = interp1( mesh.z, 1:numel(mesh.z), length/2, 'nearest' );
start = [0 MSL_height mesh.z(zidx)];
stop  = [0 0          mesh.z(zidx)];
CSX = AddBox( CSX, 'ut1', 0, start, stop );

% add a second voltage probe to compensate space offset between voltage and
% current
CSX = AddProbe( CSX, 'ut2', 0 );
start = [0 MSL_height mesh.z(zidx+1)];
stop  = [0 0          mesh.z(zidx+1)];
CSX = AddBox( CSX, 'ut2', 0, start, stop );

%% define current calc box
% current calc boxes will automatically snap to the next dual mesh-line
CSX = AddProbe( CSX, 'it1', 1 );
xidx1  = interp1( mesh.x, 1:numel(mesh.x), -MSL_width/2, 'nearest' );
xidx2  = interp1( mesh.x, 1:numel(mesh.x),  MSL_width/2, 'nearest' );
xdelta = diff(mesh.x);
yidx1  = interp1( mesh.y, 1:numel(mesh.y), MSL_height, 'nearest' );
yidx2  = interp1( mesh.y, 1:numel(mesh.y), MSL_height+1, 'nearest' );
ydelta = diff(mesh.y);
zdelta = diff(mesh.z);
start = [mesh.x(xidx1)-xdelta(xidx1-1)/2, mesh.y(yidx1)-ydelta(yidx1-1)/2, mesh.z(zidx)+zdelta(zidx)/2];
stop  = [mesh.x(xidx2)+xdelta(xidx2)/2,   mesh.y(yidx2)+ydelta(yidx2)/2,   mesh.z(zidx)+zdelta(zidx)/2];
CSX = AddBox( CSX, 'it1', 0, start, stop );

####################################################################################
#################################### SIM-RUN #######################################
####################################################################################


%% write openEMS compatible xml-file
Sim_Path_folder = strcat([mfilename '/']);
WriteOpenEMS( [Sim_Path_folder Sim_CSX], FDTD, CSX );

%% show the structure
CSXGeomPlot( [Sim_Path_folder Sim_CSX] );

%% run openEMS
openEMS_opts = '';
openEMS_opts = [openEMS_opts ' --engine=fastest'];
% openEMS_opts = [openEMS_opts ' --debug-material'];
% openEMS_opts = [openEMS_opts ' --debug-boxes'];
RunOpenEMS( mfilename, Sim_CSX, openEMS_opts );


#######################################################################################
#################################### PLOTTING #########################################
#######################################################################################


%% postprocess
freq = linspace( f0-fc, f0+fc, 501 );
U = ReadUI( {'ut1','ut2','et'}, Sim_Path_folder, freq ); % time domain/freq domain voltage
I = ReadUI( 'it1', Sim_Path_folder, freq ); % time domain/freq domain current (half time step offset is corrected)

% plot time domain voltage
hf1 = figure()
[ax,h1,h2] = plotyy( U.TD{1}.t/1e-9, U.TD{1}.val, U.TD{3}.t/1e-9, U.TD{3}.val );
set( h1, 'Linewidth', 2 );
set( h1, 'Color', [1 0 0] );
set( h2, 'Linewidth', 2 );
set( h2, 'Color', [0 0 0] );
grid on
title( 'time domain voltage' );
xlabel( 'time t / ns' );
ylabel( ax(1), 'voltage ut1 / V' );
ylabel( ax(2), 'voltage et / V' );
% now make the y-axis symmetric to y=0 (align zeros of y1 and y2)
y1 = ylim(ax(1));
y2 = ylim(ax(2));
ylim( ax(1), [-max(abs(y1)) max(abs(y1))] );
ylim( ax(2), [-max(abs(y2)) max(abs(y2))] );

% calculate characteristic impedance
% arithmetic mean of ut1 and ut2 -> voltage in the middle of ut1 and ut2
U = (U.FD{1}.val + U.FD{2}.val) / 2;
Z = U ./ I.FD{1}.val;

% plot characteristic impedance
hf2 = figure()
plot( freq/1e6, real(Z), 'k-', 'Linewidth', 2 );
hold on
grid on
plot( freq/1e6, imag(Z), 'r--', 'Linewidth', 2 );
hold on
grid on
plot( freq/1e6, abs(Z), 'g--', 'Linewidth', 2 );
title( 'characteristic impedance of MSL' );
xlabel( 'frequency f / MHz' );
ylabel( 'characteristic impedance Z / Ohm' );
legend( 'real', 'imag', 'mag');


pdf_filepath_hf1 = strcat(mfilename, "/hf1.pdf");
print (hf1, pdf_filepath_hf1, "-dpdf");

pdf_filepath_hf2 = strcat(mfilename, "/hf2.pdf");
print (hf2, pdf_filepath_hf2, "-dpdf");

#######################################################################################
#################################### COMMENTS #########################################
#######################################################################################


%% visualize electric and magnetic fields
% you will find vtk dump files in the simulation folder (tmp/)
% use paraview to visualize them
%{

%? QUESTION
Can I simulate an MSL this way and calculate the S-parameters at the same time?

%}


%! IMPEDANCE FOR MSL
% The impedance formula approximating the characteristic impedance of an MSL.

trace_thickness = 1;
substrate_height = MSL_height; 
trace_width = MSL_width;
substrate_dielectric = epsilon; # Air

function Z0 = calculate_impedance(H, W, T, Er)
    % Constants
    eta_0 = 377; % Characteristic impedance of free space in ohms (η₀)

    % Calculate Weff
    term1 = (T / pi) * log(4 * exp(1) ./ sqrt((T ./ H).^2 + (T ./ (W * pi + 1.1 * T * pi)).^2));
    Weff = W + term1 * (Er + 1) / (2 * Er);

    % Calculate X1
    X1 = 4 * (14 * Er + 8) / (11 * Er) * (H / Weff);

    % Calculate X2
    term2 = (16 * (H / Weff)^2 * ((14 * Er + 8) / (11 * Er))^2 + ((Er + 1) / (2 * Er)) * pi^2)^0.5;
    X2 = term2;

    % Calculate Z0
    Z0 = (eta_0 / (2 * pi * sqrt(2 * (Er + 1)))) * log(1 + 4 * (H / Weff) * (X1 + X2));
end

Z0 = calculate_impedance(substrate_height, trace_width, trace_thickness, substrate_dielectric);
fprintf('Characteristic impedance Z0 = %.2f ohms\n', Z0);

% https://www.allaboutcircuits.com/tools/microstrip-impedance-calculator/