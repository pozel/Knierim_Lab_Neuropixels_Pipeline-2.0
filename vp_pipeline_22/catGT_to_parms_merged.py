import glob

siteStart = 0
# siteEnd = siteStart+384
siteEnd = siteStart+32 #since WinClust supports only 32 channels right now, leave this alone
siteJitter = 0 #this is the number of sites to look before or after the end, in case the spike peak occurs further away. Should coordinate with the detect_merge_peaks later
before = 8 #setting the extraction window for WinClust. This should not change
after = 24
numBinaryFileChannels = 385 #should read this from the meta file later, since I think it can change under different configurations

# paramFileSiteStart = siteStart
# paramFileSiteEnd = siteStart+32
# imroChannelStart = 32
# imroChannelEnd = 64

basePath = r'\\Mbi-jk-scanner\D\1085_NP2\aim3\1085_02222023_cuermvl2_g0\catgt_1085_02222023_cuermvl2_g0'
dataFilePath = basePath + '\\' + '1085_02222023_cuermvl2_g0_tcat.imec0.ap.binnoMFB.bin'
matFilePath = glob.glob(basePath + '\\' + "1085_02222023_cuermvl2_g0_tcat.imec0.ap.binnoMFB_peaks.mat")[0]
channellistFile = '1085_sh0_ca1' #name, no csv tag
channellistPath = r'C:\Analysis\1085\channel_csvs_aim2' + '\\' + channellistFile + '.csv' #define channels here

outputPath = r'C:\Analysis\1085\aim3\02222023_cuermvl2' + '\\' + channellistFile

baseOutputFilename = outputPath+"\\NP"+str(siteStart)+"_to_"+str(siteEnd-1)

import numpy as np
from scipy import io
import sys
from tqdm import tqdm
from scipy.stats import stats
from functools import reduce
#import calculateParams

from multiprocessing import Pool
import time
import csv
import os
import operator


if __name__=='__mp_main__':
    distanceFile = glob.glob(basePath+"\\*-siteCoords.txt.npy")[0]
    timestamps = np.load(baseOutputFilename+"_timestamps.npy")
    sites = np.load(baseOutputFilename+"_sites.npy")
    nearbySitesFile = np.load(distanceFile)
    nearbySites = np.empty((len(nearbySitesFile), siteEnd-siteStart+1)) #PO changed from siteEnd-siteStart+1 to siteEnd-siteStart
    nearbySites[:,1:] = nearbySitesFile[:, (siteStart+1):(siteEnd+1)]
    nearbySites[:,0] = nearbySitesFile[:,0]
    jitter = 2 #for the max peak calculation. This should likely be set the same as the detect_merge_peaks parameter
    peakWindow = 4
    outputRawWaveformFileHandle = open(baseOutputFilename+".waveforms", 'rb')
    outputRawWaveformFile = np.memmap(outputRawWaveformFileHandle, 'int16', 'r', shape=(len(timestamps), siteEnd-siteStart, before+after))
    uvConversionFactors = np.load(baseOutputFilename+"_uvConversionFactors.npy")
    tiledConversionFactors = np.tile(uvConversionFactors*1000000, (siteEnd-siteStart, 1))
    
    

    
if __name__ in ['__mp_main__', '__main__']:
    outputParmsType = np.dtype([
            ('ts', '<u8'),
            ('MPeak', '<f4', (siteEnd-siteStart)),
            ('PreValley', '<f4', (siteEnd-siteStart)),
            ('SpikeID', '<f4'),
            ('Energy', '<f4', (siteEnd-siteStart)),
            ('MaxHeight', '<f4'),
            ('MaxWidth', '<f4'),
            ('PosX', '<f4'),
            ('PosY', '<f4'),
            ('tsSec', '<f4'),
            ('PostValley', '<f4', (siteEnd-siteStart))
        ])
    def calculateParams(taskIndex):#, fullWaveformPieceInput):
        fullWaveformPiece = outputRawWaveformFile[taskIndex, :, :]*tiledConversionFactors
        peakLocation = sites[taskIndex]
        output = [[0]*len(fullWaveformPiece)]*4# output[-1] = [taskIndex]*len(fullWaveformPiece)
        curWaveformPiece = fullWaveformPiece[:, before-jitter:before+jitter+1]
        if curWaveformPiece.size==0:
            return taskIndex, 0,0,0,0
        output[0] = np.max(curWaveformPiece, axis=1)#applying spatial mask for peak calculation #I THINK THIS IS THE CULPRIT!!!!!! NP 2.0
        #output[0] *= nearbySites[nearbySites[:,0]==peakLocation, 1:][0] #have to change if sitejitter changes
        curWaveformPiece = fullWaveformPiece[:, :before+jitter+1]    
        prevalleyPos = np.argmin(curWaveformPiece, axis=1)
        prevalleyPosMode = stats.mode(prevalleyPos)[0][0]
        output[1] = np.min(curWaveformPiece[:, ((prevalleyPosMode-jitter)*((prevalleyPosMode-jitter)>0)):prevalleyPosMode+3], axis=1)##******SOMETHING IS WRONG HERE FOR POSTVALLEY CALCULATION, MEMORY CONFLICT?******
        curWaveformPiece = fullWaveformPiece[:, before:]
        postvalleyPos = np.argmin(curWaveformPiece, axis=1)
        postvalleyPosMode = stats.mode(postvalleyPos)[0][0]
        output[2] = np.min(curWaveformPiece[:, ((postvalleyPosMode-jitter)*((postvalleyPosMode-jitter)>0)):postvalleyPosMode+3], axis=1)
        curWaveformPiece = fullWaveformPiece
        output[3] = np.sqrt(np.nansum(np.square(curWaveformPiece), axis=1))# return taskIndex, mpeak, prevalley, postvalley, energy
        return output

if __name__=='__main__':
    res = io.loadmat(matFilePath)
    sites = res['res']['mergedSites'][0][0].flatten()
    timestamps = res['res']['mergedTimes'][0][0].flatten()

    # timestamps = timestamps[:1398233]
    # sites = sites[:1398233]

    # timestamps, ts_unique_mask = np.unique(timestamps, return_index=True)
    # sites = sites[ts_unique_mask]

    # if len(timestamps)>3947563:
    #     print("WARNING - TOO MANY EVENTS FOR WINCLUST")
    #     print("Only 3947563 events will be processed")

    # timestamps = timestamps[:3947563]
    # sites = sites[:3947563]

    #%%

    dataBinary = np.memmap(dataFilePath, dtype='i2', mode='r')
    totalDataFrames = len(dataBinary)/numBinaryFileChannels
    if not totalDataFrames.is_integer():
        print("WARNING: YOUR BINARY FILE MAY BE CORRUPT or you are assuming you have the wrong number of channels. Check before running again!")
        sys.exit()

    dataMeta = open(dataFilePath[:-4]+".meta", 'r').readlines()
    dataMeta = {x.strip().split("=")[0]:x.strip().split("=")[1] for x in dataMeta}

    gains = np.ones(siteEnd-siteStart)
    imroTable = dataMeta['~imroTbl'].split("(")
    imroTable = np.array([list(map(int, x[:-1].split(" "))) for x in imroTable[2:]])

    with open(channellistPath, newline='') as csvfile: #PO edits, there may be a 1 off channel index error here
        channellistIdx = list(csv.reader(csvfile))

    if dataMeta['imDatPrb_type'] in ['21', '24']:
        gains*=80
        channellist = [eval(i) for i in channellistIdx[0]]
        channelID = imroTable[channellist, -1]
    else:
        gains = imroTable[siteStart:siteEnd, 3]
        channelID = np.arange(siteStart, siteEnd).astype(int)

    siteMaskStart = channellist[0]-siteJitter #BUG!! PO site mask not changing across channels
    siteMaskEnd = channellist[-1]+siteJitter
    noMask = False
    noMask_end = False
    if siteMaskStart<0:
        siteMaskStart=0
        noMask = True

    if siteMaskEnd>384: #only see if it exceeds 384, which is the max number of traces for the NP files
        siteMaskEnd=384
        noMask_end = True

    if noMask and noMask_end is True:
        masklist = channellist
    else:
        masklist = channellist
        #masklist.insert(0, siteMaskStart)
        #masklist.insert(-1, siteMaskEnd)
    #note that sites are 1-start in the input! ##HERES IS YOUR INDEXING ERROR
    #mask is the issue for NP 2.0 map!!!!! need to make True/False vector

    if dataMeta['imDatPrb_type'] in ['21', '24']:
        mask_n = []
        for n in masklist:
            mask_n.append(sites!=n)
        mask_n_mult = reduce(lambda x, y: x*y, mask_n)
        mask_n_mult_bool = list(map(operator.not_, mask_n_mult))
        mask = np.argwhere(mask_n_mult_bool).flatten()
    else:
        mask = np.argwhere((sites>=(siteMaskStart+1))*(sites<(siteMaskEnd+1))).flatten()

    sites = sites[mask]
    timestamps = timestamps[mask]

    uvConversionFactors = float(dataMeta['imAiRangeMax'])/float(dataMeta['imMaxInt'])/gains

    np.save(baseOutputFilename+"_uvConversionFactors.npy", uvConversionFactors)

    while timestamps[0]<before:
        timestamps = timestamps[1:]
        sites = sites[1:]
        print('had to remove a timestamp at bounds :(')

    while totalDataFrames-timestamps[-1]<=after:
        timestamps = timestamps[:-1]
        sites = sites[:-1]
        print('had to remove a timestamp at bounds :(')

    np.save(baseOutputFilename+"_timestamps.npy", timestamps)
    np.save(baseOutputFilename+"_sites.npy", sites)


    print("making raw waveform file...")
    if os.path.exists(baseOutputFilename+".waveforms"):
        print("waveform file exists?? not overwriting to save time")
    else:
        outputRawWaveformFileHandle = open(baseOutputFilename+".waveforms", 'wb+')
        outputRawWaveformFile = np.memmap(outputRawWaveformFileHandle, 'int16', 'w+', shape=(len(timestamps), siteEnd-siteStart, before+after))
        print(outputRawWaveformFile.shape)
        
        for spikeIdx in tqdm(range(len(timestamps))):
            # if spikeIdx > 3500:
            #     break
            # if spikeIdx%1000==999:
            #     print(spikeIdx/timestamps)
            start = (timestamps[spikeIdx].astype('uint32') - before-1)*numBinaryFileChannels
            end = (timestamps[spikeIdx].astype('uint32') + after-1)*numBinaryFileChannels
            eventData = dataBinary[start:end].reshape((before+after, numBinaryFileChannels))
            # outputRawWaveformFile[spikeIdx] = eventData[:, siteStart:siteEnd].T*-1
            for channelIdx in range(32):
                outputRawWaveformFile[spikeIdx, channelIdx] = eventData[:, channellist[channelIdx]]*-1
            
        outputRawWaveformFile.flush()
        outputRawWaveformFileHandle.close()

    print('done')

    #%%
    def calculateNearbySites(geometryPath, sites, maxDistance):
        geometryFile = np.loadtxt(open(geometryPath, 'r'))
        uniqueSites = np.unique(sites) #note that sites from the MATLAB JRClust output is 1-start index, but geometry file is 0-start
        output = np.empty((len(uniqueSites), len(geometryFile)+1), dtype=int)
        for i in range(len(uniqueSites)):
            curSite = uniqueSites[i]
            output[i,0] = curSite
            curSite+=1 #adjusting for the difference in start index here
            distances = np.square(geometryFile[:,1]-geometryFile[curSite-1, 1])
            distances += np.square(geometryFile[:,2]-geometryFile[curSite-1, 2])
            distances = np.sqrt(distances)
            output[i, 1:] = distances<maxDistance
        np.save(geometryPath+".npy", output)
        
        
    calculateNearbySites(glob.glob(basePath+"\\*-siteCoords.txt")[0], sites, 50*1.5) #using a maxDistance of 1.5x the distance in the mergePeaks algorithm

    #%% This is for testing only
    # outputRawWaveformFileHandle = open(baseOutputFilename+".waveforms", 'rb')
    # outputRawWaveformFile = np.memmap(outputRawWaveformFileHandle, 'int16', 'r', shape=(len(timestamps), siteEnd-siteStart, before+after))
    # ampMax = 300
    # startCh = 0
    # # startCh = int(96/2)
    # f, ax = plt.subplots(16, 4, figsize=(6,20))
    # spikeNum=0
    # for i in range(2):
    #     #NOTE THAT sites VARIABLE IS 1-start!
    #     # while sites[spikeNum]!=31:
    #     # while sites[spikeNum]<96 or sites[spikeNum]>=(96+32):
    #         # spikeNum+=1
    #     print(spikeNum, sites[spikeNum])
    #     for y in range(16):
    #         for x in range(4):
    #             ax[y, x].axis('off')
    #             ax[y,x].set_ylim(-1*ampMax,ampMax)
    #         ch = y+startCh
    #         if y%2:
    #             ax[y,0].plot(outputRawWaveformFile[spikeNum, ch*2])
    #             ax[y,0].axvline(7, color="#7F7F7F", alpha=0.5)
    #             ax[y,0].text(0,0, str(ch*2))            
    #             ax[y,2].plot(outputRawWaveformFile[spikeNum, ch*2+1])
    #             ax[y,2].axvline(7, color="#7F7F7F", alpha=0.5)
    #             ax[y,2].text(0,0, str(ch*2+1))            
    #         else:
    #             ax[y,1].plot(outputRawWaveformFile[spikeNum, ch*2])
    #             ax[y,1].axvline(7, color="#7F7F7F", alpha=0.5)
    #             ax[y,1].text(0,0, str(ch*2))            
    #             ax[y,3].plot(outputRawWaveformFile[spikeNum, ch*2+1])
    #             ax[y,3].axvline(7, color="#7F7F7F", alpha=0.5)
    #             ax[y,3].text(0,0, str(ch*2+1))
    #     plt.tight_layout()
    #     plt.show()
    #     # input()
    #     # plt.close('all')
    #     spikeNum+=1
        
    # outputRawWaveformFileHandle.close()



    #%%
    #actually making the parms file now



    #before this is from the pre-merged pre-pool section of the code - VP

    print("input path: ", dataFilePath)
    print("output path: ", baseOutputFilename)
    startTime = time.time()
    print(startTime)
    pool = Pool(8)
    #output = map(calculateParams, range(len(timestamps)))
    output = pool.map(calculateParams, range(len(timestamps))) ##HERE IS SECOND ISSUE FOR NP2.0 NOT LINEAR FOR ODD MAPS
    output = np.asarray(output)
    print(output.shape)
    print(time.time()-startTime)
    spikeValues = np.zeros(len(timestamps), dtype=outputParmsType)
    spikeValues['ts'] = timestamps/30000*1000*1000
    spikeValues['tsSec'] = spikeValues['ts']/1000000
    spikeValues['SpikeID'] = sites #np.arange(len(timestamps))+1
    spikeValues['MPeak'] = output[:,0]
    spikeValues['PreValley'] = output[:,1]
    spikeValues['PostValley'] = output[:,2]
    spikeValues['Energy'] = output[:,3]
    numChannels = siteEnd-siteStart
    print('writing out file')
    outputFile = open(baseOutputFilename+".Ntt.parms", 'w')
    outputFile.write("%%BEGINHEADER\n")
    outputFile.write("%Waveform Parameter File\n")
    outputFile.write("%Date: \n")
    outputFile.write("%Time: \n")
    outputFile.write("%File Type: Binary\n")
    outputFile.write("%Format:\n")
    outputFile.write("%--------------------------\n")
    outputFile.write("%|  TimeStamp  (8 bytes)  |\n")
    outputFile.write("%-------------------------|\n")
    for i in range(numChannels):
        outputFile.write("%|  MPeak-{0}  (Single)  |\n".format(i+1))
        outputFile.write("%-------------------------|\n")
    for i in range(numChannels):
        outputFile.write("%|  PreValley-{0}  (Single)  |\n".format(i+1))
        outputFile.write("%-------------------------|\n") 
    outputFile.write("%|  SpikeID  (Single)  |\n")
    outputFile.write("%-------------------------|\n")
    for i in range(numChannels):
        outputFile.write("%|  Energy-{0}  (Single)  |\n".format(i+1))
        outputFile.write("%-------------------------|\n")
    outputFile.write("%|  MaxHeight (Single)  |\n")
    outputFile.write("%-------------------------|\n")
    outputFile.write("%|  MaxWidth (Single)  |\n")
    outputFile.write("%-------------------------|\n")
    outputFile.write("%|  PosX (Single)  |\n")
    outputFile.write("%-------------------------|\n")
    outputFile.write("%|  PosY (Single)  |\n")
    outputFile.write("%-------------------------|\n")
    outputFile.write("%|  TimeStamp (seconds) (Single)  |\n")
    outputFile.write("%-------------------------|\n")
    for i in range(numChannels):
        outputFile.write("%|  PostValley-{0}  (Single)  |\n".format(i+1))
        outputFile.write("%-------------------------|\n")
    outputFile.write("%Timestamp,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,MPeak-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,PreValley-,SpikeID,Energy-1,Energy-2,Energy-3,Energy-4,Energy-5,Energy-6,Energy-7,Energy-8,Energy-9,Energy-10,Energy-11,Energy-12,Energy-13,Energy-14,Energy-15,Energy-16,Energy-17,Energy-18,Energy-19,Energy-20,Energy-21,Energy-22,Energy-23,Energy-24,Energy-25,Energy-26,Energy-27,Energy-28,Energy-29,Energy-30,Energy-31,Energy-32,MaxHeight,MaxWidth,PosX,PosY,Timestamp, Valley-1,Valley-2,Valley-3,Valley-4,Valley-5,Valley-6,Valley-7,Valley-8,Valley-9,Valley-10,Valley-11,Valley-12,Valley-13,Valley-14,Valley-15,Valley-16,Valley-17,Valley-18,Valley-19,Valley-20,Valley-21,Valley-22,Valley-23,Valley-24,Valley-25,Valley-26,Valley-27,Valley-28,Valley-29,Valley-30,Valley-31,Valley-32%\n")
    outputFile.write("%%ENDHEADER\n")
    spikeValues.tofile(outputFile)
    outputFile.close();

#%%