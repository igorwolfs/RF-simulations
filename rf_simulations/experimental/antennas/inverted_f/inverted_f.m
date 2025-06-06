%
% EXAMPLE / antennas / inverted-f antenna (ifa) 2.4GHz
%
% This example demonstrates how to:
%  - calculate the reflection coefficient of an ifa
%  - calculate farfield of an ifa
%
% Tested with
%  - Octave 3.7.5
%  - openEMS v0.0.30+ (git 10.07.2013)
%
% (C) 2013 Stefan Mahr <dac922@gmx.de>

#######################################################################################
##################################### INTRO ###########################################
#######################################################################################

%
% EXAMPLE / antennas / inverted-f antenna (ifa) 2.4GHz
%
% This example demonstrates how to:
%  - calculate the reflection coefficient of an ifa
%  - calculate farfield of an ifa
%
% Tested with
%  - Octave 3.7.5
%  - openEMS v0.0.30+ (git 10.07.2013)
%

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

%% setup the simulation
physical_constants;
unit = 1e-3; % all length in mm
%% setup FDTD parameter & excitation function
f0 = 2.5e9; % center frequency
fc = 1e9; % 20 dB corner frequency

###############################################################################################
###################################### INITIALIZE FDTD ########################################
###############################################################################################


max_timesteps = 60000;
FDTD = InitFDTD('NrTS',  max_timesteps );

#############################################################################################
################################# BOUNDARY CONDITIONS #######################################
#############################################################################################
BC = {'MUR' 'MUR' 'MUR' 'MUR' 'MUR' 'MUR'}; % boundary conditions
FDTD = SetBoundaryCond( FDTD, BC );

#####################################################################################
################################# GRID / MESH #######################################
#####################################################################################

CSX = InitCSX();
mesh.x = [];
mesh.y = [];
mesh.z = [];

%!############################## SUBSTRATE ######################################

substrate.width  = 80;             % width of substrate
substrate.length = 80;             % length of substrate
substrate.thickness = 1.5;         % thickness of substrate
substrate.cells = 4;               % use 4 cells for meshing substrate

% substrate setup
substrate.epsR   = 4.3;
substrate.kappa  = 1e-3 * 2*pi*2.45e9 * EPS0*substrate.epsR;

% size of the simulation box
SimBox = [substrate.width*2 substrate.length*2 150];

%% create substrate
CSX = AddMaterial( CSX, 'substrate');
CSX = SetMaterialProperty( CSX, 'substrate', 'Epsilon',substrate.epsR, 'Kappa', substrate.kappa);

start = [-substrate.width/2  -substrate.length/2                    0];
stop  = [ substrate.width/2   substrate.length/2  substrate.thickness];
CSX = AddBox( CSX, 'substrate', 1, start, stop );
% add extra cells to discretize the substrate thickness
mesh.z = [linspace(0,substrate.thickness,substrate.cells+1) mesh.z];


%!############################## IFA ######################################

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                substrate.width
%  _______________________________________________    __ substrate.
% | A                        ifa.l                |\  __    thickness
% | |ifa.e         __________________________     | |
% | |             |    ___  _________________| w2 | |
% | |       ifa.h |   |   ||                      | |
% |_V_____________|___|___||______________________| |
% |                .w1   .wf\                     | |
% |                   |.fp|  \                    | |
% |                       |    feed point         | |
% |                       |                       | | substrate.length
% |<- substrate.width/2 ->|                       | |
% |                                               | |
% |_______________________________________________| |
%  \_______________________________________________\|
%
% Note: It's not checked whether your settings make sense, so check
%       graphical output carefully.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


ifa.h  = 8;            % height of short circuit stub
ifa.l  = 22.5;         % length of radiating element
ifa.w1 = 4;            % width of short circuit stub
ifa.w2 = 2.5;          % width of radiating element
ifa.wf = 1;            % width of feed element
ifa.fp = 4;            % position of feed element relative to short
                       %  circuit stub
ifa.e  = 10;           % distance to edge



%open AppCSXCAD and show ifa
show = 1;


%!############################## MESH ######################################

%initialize the mesh with the "air-box" dimensions
mesh.x = [-SimBox(1)/2 SimBox(1)/2];
mesh.y = [-SimBox(2)/2 SimBox(2)/2];
mesh.z = [-SimBox(3)/2 SimBox(3)/2];

%% create ground plane -> Groundplane connected to IFA
CSX = AddMetal( CSX, 'groundplane' ); % create a perfect electric conductor (PEC)
start = [-substrate.width/2  -substrate.length/2        substrate.thickness];
stop  = [ substrate.width/2   substrate.length/2-ifa.e  substrate.thickness];
CSX = AddBox(CSX, 'groundplane', 10, start,stop);

%% create ifa -> Create the inverted f-antenna creation. (height is 0)
CSX = AddMetal( CSX, 'ifa' ); % create a perfect electric conductor (PEC)
tl = [0,substrate.length/2-ifa.e,substrate.thickness];   % translate

start = [0 0.5 0] + tl;
stop = start + [ifa.wf ifa.h-0.5 0];
CSX = AddBox( CSX, 'ifa', 10,  start, stop);  % feed element


start = [-ifa.fp 0 0] + tl;
stop =  start + [-ifa.w1 ifa.h 0];
CSX = AddBox( CSX, 'ifa', 10,  start, stop);  % short circuit stub

start = [(-ifa.fp-ifa.w1) ifa.h 0] + tl;
stop = start + [ifa.l -ifa.w2 0];
CSX = AddBox( CSX, 'ifa', 10, start, stop);   % radiating element

ifa_mesh = DetectEdges(CSX, [], 'SetProperty','ifa');
mesh.x = [mesh.x SmoothMeshLines(ifa_mesh.x, 0.5)];
mesh.y = [mesh.y SmoothMeshLines(ifa_mesh.y, 0.5)];

%% finalize the mesh
% generate a smooth mesh with max. cell size: lambda_min / 20
mesh = DetectEdges(CSX, mesh);
mesh = SmoothMesh(mesh, c0 / (f0+fc) / unit / 20);
CSX = DefineRectGrid(CSX, unit, mesh);

####################################################################################
################################# EXCITATION #######################################
####################################################################################

FDTD = SetGaussExcite( FDTD, f0, fc );

%% apply the excitation & resist as a current source
% port is in the y-direction on the lower bar.
% port resist is also added at the same place as the excitation, connecting to the inverted F-box.
start = [0 0 0] + tl;
stop  = start + [ifa.wf 0.5 0];
feed.R = 50;     % feed resistance
[CSX port] = AddLumpedPort(CSX, 5 ,1 ,feed.R, start, stop, [0 1 0], true);


####################################################################################
#################################### DUMPS #########################################
####################################################################################


%% add a nf2ff calc box; size is 3 cells away from MUR boundary condition
start = [mesh.x(4)     mesh.y(4)     mesh.z(4)];
stop  = [mesh.x(end-3) mesh.y(end-3) mesh.z(end-3)];
[CSX nf2ff] = CreateNF2FFBox(CSX, 'nf2ff', start, stop);


%% prepare simulation folder
plot_path = strcat(mfilename);
Sim_Path = strcat(plot_path, "/", mfilename);
Sim_CSX = strcat([mfilename 'xml']);

[status, message, messageid] = rmdir( Sim_Path, 's' ); % clear previous directory
[status, message, messageid] = rmdir( plot_path, 's' ); % clear previous directory

[status, message, messageid] = mkdir( plot_path ); % create empty simulation folder
[status, message, messageid] = mkdir( Sim_Path ); % create empty simulation folder


####################################################################################
#################################### SIM-RUN #######################################
####################################################################################

%% write openEMS compatible xml-file
WriteOpenEMS( [Sim_Path '/' Sim_CSX], FDTD, CSX );

%% show the structure
if (show == 1)
  CSXGeomPlot( [Sim_Path '/' Sim_CSX] );
end


%% run openEMS
RunOpenEMS( Sim_Path, Sim_CSX, "verbose", 3);  %RunOpenEMS( Sim_Path, Sim_CSX, '--debug-PEC -v');


%% postprocessing & do the plots
freq = linspace( max([1e9,f0-fc]), f0+fc, 501 );
port = calcPort(port, Sim_Path, freq);

P_in = real(0.5 * port.uf.tot .* conj( port.if.tot )); % antenna feed power


Zin = port.uf.tot ./ port.if.tot;
% plot feed point impedance
hf = figure
plot( freq/1e6, real(Zin), 'k-', 'Linewidth', 2 );
hold on
grid on
plot( freq/1e6, imag(Zin), 'r--', 'Linewidth', 2 );
title( 'feed point impedance' );
xlabel( 'frequency f / MHz' );
ylabel( 'impedance Z_{in} / Ohm' );
legend( 'real', 'imag' );
save_path = strcat(plot_path, '/', 'impedance', '.pdf');
print (hf, save_path, "-dpdf");

close all;

% plot reflection coefficient S11
s11 = port.uf.ref ./ port.uf.inc;

hf = figure
plot( freq/1e6, 20*log10(abs(s11)), 'k-', 'Linewidth', 2 );
grid on
title( 'reflection coefficient S_{11}' );
xlabel( 'frequency f / MHz' );
ylabel( 'reflection coefficient |S_{11}|' );

save_path = strcat(plot_path, '/', 's_parameters', '.pdf');
print (hf, save_path, "-dpdf");
close all;

%% NFFF contour plots %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%find resonance frequency from s11
f_res_ind = find(s11==min(s11));
f_res = freq(f_res_ind);

%%
disp( 'calculating 3D far field pattern and dumping to vtk (use Paraview to visualize)...' );
thetaRange = (0:2:180);
phiRange = (0:2:360) - 180;
nf2ff = CalcNF2FF(nf2ff, Sim_Path, f_res, thetaRange*pi/180, phiRange*pi/180);

%{
figure()
# Normalize electric field + add directivity to scale the plot so the highest value shows the actual max directivity.
E_norm = 20.0*np.log10(nf2ff_res.E_norm(1)/np.max(nf2ff_res.E_norm(1))) + 10.0*np.log10(nf2ff_res.Dmax(1)));
plot(theta, np.squeeze(E_norm(:,0)), 'k-', linewidth=2, label='xz-plane')
plot(theta, np.squeeze(E_norm(:,1)), 'r--', linewidth=2, label='yz-plane')
grid()
ylabel('Directivity (dBi)')
xlabel('Theta (deg)')
title('Frequency: {} GHz'.format(f_res/1e9))
legend()
plt.savefig(os.path.join(Plot_Path, 'e_field_resonance.pdf'));


% display power and directivity
disp( ['radiated power: Prad = ' num2str(nf2ff.Prad) ' Watt']);
disp( ['directivity: Dmax = ' num2str(nf2ff.Dmax) ' (' num2str(10*log10(nf2ff.Dmax)) ' dBi)'] );
disp( ['efficiency: nu_rad = ' num2str(100*nf2ff.Prad./real(P_in(f_res_ind))) ' %']);

E_far_normalized = nf2ff.E_norm{1} / max(nf2ff.E_norm{1}(:)) * nf2ff.Dmax;
DumpFF2VTK([Sim_Path '/3D_Pattern.vtk'],E_far_normalized,thetaRange,phiRange,1e-3);
%}