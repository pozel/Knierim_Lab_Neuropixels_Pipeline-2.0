%% Run All Pipeline 2.0
% Written by: PO, March 2023
% ***Make sure you have a lot of RAM space for the following steps.***
function [dataPath] = runall_Pipeline2(dataPath)
beep on;
%% Run All Preprocessing Steps
% To customize, see 'EDIT' sections in individual functions.

% The path you're going to pick is either in example format 1)
% C:\animal#\experiment# or 2) C:\animal#\experiment#\imecrecording#_g0

% DO NOT RUN THIS ON ACROSS ALL ANIMALS, AS IT HAS NOT BEEN TESTED (e.g.
% C:\animal#)

[dataPath] = uigetdir('*','Select Raw Parent Data Folder.');
[dataPath] = runall_CatGT(dataPath);
[dataPath] = runall_TPrime(dataPath);
beep;

%% Run Artifact Removal Steps (for PO)
% To customize, see 'EDIT' sections in individual functions.

% [dataPath] = runall_StimRemoval(dataPath);
%beep;

%% Run Spike Identification Steps
% To customize, see 'EDIT' sections in individual functions.

% [dataPath] = runall_Coords(dataPath);
% [dataPath] = runall_DetectPeaks(dataPath);
%runall_CalcParms(dataPath);
beep;

beep off;
end