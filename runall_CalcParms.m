%% Run All catGT_to_parms_merged.m in Folder
% Note: Run after detect peaks and coords
% Written by: PO, March 2023
function runall_CalcParms(datapath)
%EDIT add path to pipeline 2.0 here
setenv('C:\Analysis\Winclust Pipeline\vp_pipeline_22');
datapath=datapath;
all_data_files = ["1085_02222023_cuermvl2_g0", "1085_02232023_cuermvl1_g0", "1085_02232023_cuermvl2_g0", "1085_02232023_cuermvl3_g0", "1085_02242023_cuermvl1_g0", "1085_02242023_cuermvl2_g0", "1085_02242023_cuermvl3_g0", "1085_02232023_cuermvl3pt2_g0"];
all_save_files = ["02222023_cuermvl2", "02232023_cuermvl1", "02232023_cuermvl2", "02232023_cuermvl3", "02242023_cuermvl1", "02242023_cuermvl2", "02242023_cuermvl3", "02232023_cuermvl3pt2"];
all_channels_list = ["1085_sh0_ca1", "1085_sh0_ca3", "1085_sh0_uca3", "1085_sh1_ca1", "1085_sh1_ca3", "1085_sh1_uca3", "1085_sh2_ca1", "1085_sh2_ca3", "1085_sh2_uca3", '1085_sh3_ca1', "1085_sh3_ca3", "1085_sh3_uca3"];
all_data_outputPath = "C:\Analysis\1085\aim3\";
all_data_subdir = "\\Mbi-jk-scanner\D\1085_NP2\aim3\";

for i = 1:length(all_data_files)
    for j = 1:length(all_channels_list)

        basePath = [all_data_subdir all_data_files(i) "\catgt_" all_data_files(i)]; % we loop through this in loop A
        basePath = join(basePath,"");
        channellistFile = all_channels_list(j); % we loop through this in loop B
        outputPath = [all_data_outputPath all_save_files(i)]; % we loop through this in loop B
        outputPath = join(outputPath,"");
        
        sys_string = ['python catGT_to_parms_merged.py ' basePath ' ' channellistFile ' ' outputPath];
        sys_string = join(sys_string,"");
        system(sys_string);
    end
end
end