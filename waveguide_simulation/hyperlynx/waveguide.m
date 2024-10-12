close all
clear
clc


addpath('~/opt/openEMS/share/openEMS/matlab');
addpath('~/opt/openEMS/share/CSXCAD/matlab');
addpath('~/opt/openEMS/share/hyp2mat/matlab');

physical_constants;
f_max = 7e9;

# ******* CSXCAD ********
CSX = InitCSX();
CSX = ImportHyperLynx(CSX, 'waveguide.hyp');

[port1_material, port1_start, port1_stop] = GetHyperLynxPort(CSX, 'TP1.1');
[port2_material, port2_start, port2_stop] = GetHyperLynxPort(CSX, 'TP2.1');

disp(port1_start)
disp(port1_stop)
display(port1_material)e
disp(port2_start)
disp(port2_stop)AddLumpedPort