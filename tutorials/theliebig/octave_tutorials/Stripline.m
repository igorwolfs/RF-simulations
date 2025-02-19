% example demonstrating the use of a stripline terminated by the pml
% (c) 2013 Thorsten Liebig

close all
clear
clc


addpath('~/opt/openEMS/share/openEMS/matlab');
addpath('~/opt/openEMS/share/CSXCAD/matlab');
addpath('~/opt/openEMS/share/hyp2mat/matlab');

%% setup the simulation %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
physical_constants;
unit = 1e-6; % specify everything in um
SL_length = 50000;
SL_width = 520;
SL_height = 500;
substrate_thickness = SL_height;
substrate_epr = 3.66;
f_max = 7e9;

%% setup FDTD parameters & excitation function %%%%%%%%%%%%%%%%%%%%%%%%%%%%
FDTD = InitFDTD();
FDTD = SetGaussExcite( FDTD, f_max/2, f_max/2 );
BC   = {'PML_8' 'PML_8' 'PMC' 'PMC' 'PEC' 'PEC'};
FDTD = SetBoundaryCond( FDTD, BC );

%% setup CSXCAD geometry & mesh %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CSX = InitCSX();
resolution = c0/(f_max*sqrt(substrate_epr))/unit /50; % resolution of lambda/50
mesh.x = SmoothMeshLines( [-SL_length/2 0 SL_length/2], resolution, 1.5 ,0 );
mesh.y = SmoothMeshLines( [0 SL_width/2+[-resolution/3 +resolution/3*2]/4], resolution/4 , 1.5 ,0);
mesh.y = SmoothMeshLines( [-10*SL_width -mesh.y mesh.y 10*SL_width], resolution, 1.3 ,0);
mesh.z = linspace(0,substrate_thickness,5);
mesh.z = sort(unique([mesh.z -mesh.z]));
CSX = DefineRectGrid( CSX, unit, mesh );

%% substrate
CSX = AddMaterial( CSX, 'RO4350B' );
CSX = SetMaterialProperty( CSX, 'RO4350B', 'Epsilon', substrate_epr );
start = [mesh.x(1),   mesh.y(1),   mesh.z(1)];
stop  = [mesh.x(end), mesh.y(end), mesh.z(end)];
CSX = AddBox( CSX, 'RO4350B', 0, start, stop );

%% SL port
CSX = AddMetal( CSX, 'PEC' );
portstart = [ mesh.x(1), -SL_width/2, 0];
portstop  = [ 0,         SL_width/2, 0];
[CSX,port{1}] = AddStripLinePort( CSX, 999, 1, 'PEC', portstart, portstop, SL_height, 'x', [0 0 -1], 'ExcitePort', true, 'FeedShift', 10*resolution, 'MeasPlaneShift',  SL_length/3);

portstart = [mesh.x(end), -SL_width/2, 0];
portstop  = [0          ,  SL_width/2, 0];
[CSX,port{2}] = AddStripLinePort( CSX, 999, 2, 'PEC', portstart, portstop, SL_height, 'x', [0 0 -1], 'MeasPlaneShift',  SL_length/3 );

%% write/show/run the openEMS compatible xml-file
plot_path = strcat(mfilename);
Sim_Path = strcat(plot_path, "/", mfilename);
Sim_CSX = 'stripline.xml';

[status, message, messageid] = rmdir( Sim_Path, 's' ); % clear previous directory
[status, message, messageid] = rmdir( plot_path, 's' ); % clear previous directory

[status, message, messageid] = mkdir( plot_path ); % create empty simulation folder
[status, message, messageid] = mkdir( Sim_Path ); % create empty simulation folder

WriteOpenEMS( [Sim_Path '/' Sim_CSX], FDTD, CSX );
CSXGeomPlot( [Sim_Path '/' Sim_CSX] );
RunOpenEMS( Sim_Path, Sim_CSX );

%%% post-processing
%% S-parameters
close all
f = linspace( 1e6, f_max, 1601 );
port = calcPort( port, Sim_Path, f, 'RefImpedance', 50);

s11 = port{1}.uf.ref./ port{1}.uf.inc;
s21 = port{2}.uf.ref./ port{1}.uf.inc;

hf = figure 
plot(f/1e9,20*log10(abs(s11)),'k-','LineWidth',2);
hold on;
grid on;
plot(f/1e9,20*log10(abs(s21)),'r--','LineWidth',2);
legend('S_{11}','S_{21}');
ylabel('S-Parameter (dB)','FontSize',12);
xlabel('frequency (GHz) \rightarrow','FontSize',12);
ylim([-50 2]);

save_path = strcat(plot_path, '/', 's_parameters', '.pdf');
print (hf, save_path, "-dpdf");

%% uf_inc
close all;

hf = figure

[hAx,hLine1,hLine2] = plotyy(f/1e9, port{1}.uf.ref, f/1e9, port{2}.uf.ref);

ylabel(hAx(1),"port1_uf_ref"); % left y-axis 
ylabel(hAx(2),"port2_uf_ref"); % right y-axis
legend('uf_ref_1','uf_ref_2');
xlabel('frequency (GHz) \rightarrow','FontSize',12);
save_path = strcat(plot_path, '/', 'voltage_ref', '.pdf');
print (hf, save_path, "-dpdf");

%% uf_inc
close all;

hf = figure

[hAx,hLine1,hLine2] = plotyy(f/1e9, port{1}.uf.inc, f/1e9, port{2}.uf.inc);

ylabel(hAx(1),"port1_uf_inc"); % left y-axis 
ylabel(hAx(2),"port2_uf_inc"); % right y-axis
legend('port1_uf_inc','port2_uf_inc');
xlabel('frequency (GHz) \rightarrow','FontSize',12);
save_path = strcat(plot_path, '/', 'voltage_inc', '.pdf');
print (hf, save_path, "-dpdf");


%% uf_tot
close all

hf = figure
plot(f/1e9, port{1}.uf.tot,'k-','LineWidth',2);
hold on;
grid on;
plot(f/1e9, port{2}.uf.tot,'r--','LineWidth',2);

title("port uf tot")
legend('uf_in_tot','uf_out_tot');
xlabel('frequency (GHz) \rightarrow','FontSize',12);
save_path = strcat(plot_path, '/', 'uf_tot', '.pdf');
print (hf, save_path, "-dpdf");

%% uf_tot
close all

hf = figure
title("port if tot")
plot(f/1e9, port{1}.if.tot,'k-','LineWidth',2);
hold on;
grid on;
plot(f/1e9, port{2}.if.tot,'r--','LineWidth',2);
legend('if_in_tot','if_out_tot');
xlabel('frequency (GHz) \rightarrow','FontSize',12);
save_path = strcat(plot_path, '/', 'if_tot', '.pdf');
print (hf, save_path, "-dpdf");

%% RAW U 

close all
hf = figure

plot(f/1e9, port{1}.raw.U.FD{2}.val,'k-','LineWidth',2);
hold on;
grid on;
plot(f/1e9,  port{2}.raw.U.FD{2}.val,'r--','LineWidth',2);
legend('uf_raw_in','uf_raw_out');
xlabel('frequency (GHz) \rightarrow','FontSize',12);
save_path = strcat(plot_path, "/", 'uf_raw', '.pdf');
print (hf, save_path, "-dpdf");

%% RAW I

close all
hf = figure

plot(f/1e9, port{1}.raw.I.FD{1}.val,'k-','LineWidth',2);
hold on;
grid on;
plot(f/1e9,  port{2}.raw.I.FD{1}.val,'r--','LineWidth',2);
legend('if_raw_in','if_raw_out');
ylabel('S-Parameter (dB)','FontSize',12);
xlabel('frequency (GHz) \rightarrow','FontSize',12);
save_path = strcat(plot_path, '/', 'if_raw', ".pdf");
print (hf, save_path, "-dpdf");


%{
close all
figure
[hAx,hLine1,hLine2] = plotyy(f/1e9, port{1}.raw.U.FD{2}.val, f/1e9, port{2}.raw.U.FD{2}.val);
title("port uf raw")
ylabel(hAx(1),"uf_raw_in") % left y-axis 
ylabel(hAx(2),"uf_raw_out") % right y-axis
% hLine1.LineStyle = "--";
% hLine2.LineStyle = ":";
legend('uf_raw_in','uf_raw_out');
xlabel('frequency (GHz) \rightarrow','FontSize',12);
print -djpg uf_raw


close all
figure
title("port if raw")
ylabel(hAx(1),"if_raw_in") % left y-axis 
ylabel(hAx(2),"if_raw_out") % right y-axis
% hLine1.LineStyle = "--";
% hLine2.LineStyle = ":";
legend('if_raw_in','if_raw_out');
xlabel('frequency (GHz) \rightarrow','FontSize',12);
print -djpg if_raw
%}