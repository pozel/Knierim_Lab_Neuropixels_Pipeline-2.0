%% Run All Coords in Folder
% Written by: PO, March 2023
function [dataPath] = runall_DetectPeaks(dataPath)

% Find subfolders of raw data
allFiles = rdir(dataPath);
allFiles_str = string(allFiles);
p=1;
k=1;
for i = 1:length(allFiles_str)
    %get ap.bin file
    if isempty(strfind(allFiles_str{i,1},'txt')) && ~isempty(strfind(allFiles_str{i,1},'ap.bin')) && ~isempty(strfind(allFiles_str{i,1},'tcat')) && isempty(strfind(allFiles_str{i,1},'peaks')) && isempty(strfind(allFiles_str{i,1},'meta'))
        tempFile = allFiles_str{i,1};
        extractedpath = join([extractBefore(tempFile,'catgt') 'catgt' extractBetween(tempFile,'catgt','\') '\'],'');
        fileName{k,1} = erase(tempFile,extractedpath{:});
        fileDir{k,1} = extractedpath{:};
        k=k+1;
    elseif ~isempty(strfind(allFiles_str{i,1},'siteCoords.txt')) && isempty(strfind(allFiles_str{i,1},'npy'))%get coordinate file
        tempFile2 = allFiles_str{i,1};
        extractedpath2 = join([extractBefore(tempFile2,'catgt') 'catgt' extractBetween(tempFile2,'catgt','\') '\'],'');
        coordName{p,1} =  erase(tempFile2,extractedpath2{:});
        coordDir{p,1} = extractedpath2{:};
        p=p+1;
    else
        %pass
    end
end

%% Run detect_merge_peaks.m

for ii = 1:length(fileName)
    try
        detect_merge_peaks(fileName{ii},fileDir{ii},coordName{ii},coordDir{ii});
        close all; %figures generated are not saved
        display(sprintf('Finished creating peaks file for %s.\n',fileName{ii,1})); %#ok<*DSPS> 
    catch
        display(sprintf('No ap.bin found for %s',fileName{ii,1}));
    end
end
    
end
