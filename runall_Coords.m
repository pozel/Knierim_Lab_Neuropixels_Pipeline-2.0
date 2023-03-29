%% Run All Coords in Folder
% Written by: PO, March 2023
function [dataPath] = runall_Coords(dataPath)

%% Get all files that need to run through SGLXMetaToCoords.m

% Find subfolders of raw data
allFiles = rdir(dataPath);
allFiles_str = string(allFiles);
p=1;
for i = 1:length(allFiles_str)
    %get Coords path, need metadata file
    if ~isempty(strfind(allFiles_str{i,1},'.meta')) && ~isempty(strfind(allFiles_str{i,1},'ap')) && ~isempty(strfind(allFiles_str{i,1},'tcat'))
        MetaFiles = allFiles_str{i,1};
        extractedpath = join([extractBefore(MetaFiles,'catgt') 'catgt' extractBetween(MetaFiles,'catgt','\') '\'],'');
        CoordsPath{p,1} = extractedpath{:};
        CoordsFiles{p,1} = erase(MetaFiles,extractedpath{:});
        p=p+1;
    else
        %pass
    end
end

%% Run SGLXMetaToCoords.m

for ii = 1:length(CoordsFiles)
    cd(CoordsPath{ii});
    SGLXMetaToCoords(CoordsFiles{ii},CoordsPath{ii});
    close all; %figures generated are not saved
    display(sprintf('Finished creating coordinates file for %s.\n',CoordsPath{ii})); %#ok<*DSPS> 
end
end