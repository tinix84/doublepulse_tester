%% how to import log file of LTspice into mat file
% clear all
% close all
% clc

% load EPC2001

% filename = './DoublePulseTester_EPC8009_sync.log'; %filename of LTspice output log
% %please log file attached as example
% startRow_step_description = 11; %line number of first .step declaration
% endRow_step_description = 58; %line number of first .step declaration
% startRow_Eon = 63; %start line number of Eon losses section
% endRow_Eon = 100; %end line number of Eon losses section
% startRow_Eoff = 116; %start line number of Eoff losses section
% endRow_Eoff = 163; %end line number of Eon losses section

% % with the line numbers above we parse the log file of LTspice
% % to have back 4 vector [current, voltage, Eon, Eoff]
% IV_mat = importfile_step_descr(filename, startRow_step_description, endRow_step_description);
% I=IV_mat(:,1); V=IV_mat(:,2);
% Eon = importfile_Eon(filename, startRow_Eon, endRow_Eon);
% Eoff = importfile_Eoff(filename, startRow_Eoff, endRow_Eoff);

%import csv py
% I=tbl.current;V=tbl.voltage; Eon=tbl.eon; Eoff=tbl.eoff;

% we convert the 4 vector in a grid to plot the mesh surface
[I_mesh,V_mesh,Eon_mesh] = xyz2grid(I, V, Eon); 
[I_mesh,V_mesh,Eoff_mesh] = xyz2grid(I, V, Eoff);

% we save the results in a mat file
% save('Eloss.mat', 'I_mesh','V_mesh','Eon_mesh', 'Eoff_mesh')
clear IV_mat
save('Eloss.mat', 'I','V','Eon', 'Eoff','I_mesh','V_mesh','Eon_mesh', 'Eoff_mesh')

%% how to plot the mat file in a surface
clear all
close all
clc

load('Eloss.mat')
surf(I_mesh,V_mesh,Eon_mesh,'FaceAlpha',0.5)
title('On switching losses')
xlabel('Current [A]')
ylabel('Voltage [V]')
zlabel('Energy [J]')

figure
surf(I_mesh,V_mesh,Eoff_mesh,'FaceAlpha',0.5)
title('Off switching losses')
xlabel('Current [A]')
ylabel('Voltage [V]')
zlabel('Energy [J]')


%% how to get losses for different value than the grid
clear all
close all
clc

load('Eloss.mat')
Vq=20 % switching voltage required
Iq=5 % switching current required
Eonq= griddata(I_mesh,V_mesh,Eon_mesh,Iq,Vq) % Eon linear interpolated from grid
Eoffq = griddata(I_mesh,V_mesh,Eoff_mesh,Iq,Vq) % Eoff linear interpolated from grid
