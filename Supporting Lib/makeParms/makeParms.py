# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 15:52:38 2019

@author: vyash
"""

import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import stats
import sys

combineDiff = 2
numChannels = 32
jitter = 2

outputParmsType = np.dtype([
        ('ts', '<u8'),
        ('MPeak', '<f4', (numChannels)),
        ('PreValley', '<f4', (numChannels)),
        ('SpikeID', '<f4'),
        ('Energy', '<f4', (numChannels)),
        ('MaxHeight', '<f4'),
        ('MaxWidth', '<f4'),
        ('PosX', '<f4'),
        ('PosY', '<f4'),
        ('tsSec', '<f4'),
        ('PostValley', '<f4', (numChannels))
    ])

#parmsType = np.dtype([
#    ('ts', '<u8'),
#    ('MPeak', '<f4', (4)),
#    ('PreValley', '<f4', (4)),
#    ('SpikeID', '<f4'),
#    ('Energy', '<f4', (4)),
#    ('MaxHeight', '<f4'),
#    ('MaxWidth', '<f4'),
#    ('PosX', '<f4'),
#    ('PosY', '<f4'),
#    ('tsSec', '<f4'),
#    ('Peak', '<f4', (4)),
#    ('Valley', '<f4', (4)),
#    ('empty', '<f4', (11, ))
#])

path = sys.argv[1]
# path = "S:\\PPG Pilot Animals\\1910-33_Acorn\\2019-12-06_12-07-11\\B_50B\\"
if len(sys.argv)==2:    
    pathFolder = sys.argv[1].split("\\")[-1].split("_")
    shank = pathFolder[0]
    threshold = pathFolder[1]
    # shank = input("current shank: ")
    # threshold = input("threshold: ")
else:
    shank = sys.argv[2]
    threshold = sys.argv[3]

before = 8
after = 24


peakTimepoints = np.load(path+"\\peakTimepoints_"+shank+"_"+threshold+".npy")
#peakTimepointsFileList = np.load(path+"peakTimepointsFileList_A.npy")
# channelData = np.load(path+"\\expandedCSC_"+shank+".npy", mmap_mode='r')
channelData = np.memmap(path+"\\expandedCSC_"+shank+".memmap", dtype='float64', mode='r')
inputFileListLen = len(np.load(sys.argv[1]+"\\peakTimepointsInputFileList_"+shank+"_"+threshold+".npy"))
channelData = np.reshape(channelData, (inputFileListLen, int(len(channelData)/inputFileListLen)))



#peakTimepointsDiff = np.diff(peakTimepoints)
# peakTimepointsDiff = np.append([999999], peakTimepointsDiff)

#plt.hist(peakTimepointsDiff, bins=100, range=[0,100])
#plt.show()

#singleTSDiff = (peakTimepointsDiff==7).astype(int)
#
#stringSingleDiffs =  "".join(map(str, singleTSDiff))
##print(stringSingleDiffs)
#for i in range(100,0,-1):
#    searchStr = "1"*i
#    print(i, stringSingleDiffs.count(searchStr))
#
newPeakTimepoints = []


lastTimepoint = -9999;

for timepoint in peakTimepoints:
    if (timepoint-lastTimepoint)>combineDiff:
        newPeakTimepoints.append(timepoint)
        lastTimepoint = timepoint
        
print(len(peakTimepoints), len(newPeakTimepoints))
        
#sys.exit()

#newPeakTimepoints = newPeakTimepoints[:31595]
spikeValues = np.zeros(len(newPeakTimepoints), dtype=outputParmsType)

#cscFiles = []
#
#for i in range(numChannels):
#    cscFiles.append(np.load(path+"\\CSC_A"+str(i+1)+".npz")['data'])

def calculateParams(timepointIdx, timepoint, data, before, after):
    if (timepoint-before)<0:
        before=timepoint        
    fullWaveformPiece = data[:, timepoint-before:timepoint+after]
    if(fullWaveformPiece.shape[1]!=32):
        print("oh no!", timepointIdx, fullWaveformPiece.shape)
    outputRawWaveformFile[timepointIdx, :, :fullWaveformPiece.shape[1]] = fullWaveformPiece
    # f, ax = plt.subplots(16,2)
    # [ax[i,0].plot(fullWaveformPiece[i*2]) for i in range(16)]
    # [ax[i,1].plot(fullWaveformPiece[1+i*2]) for i in range(16)]
    # plt.show()
        
    curWaveformPiece = fullWaveformPiece[:, before-jitter:before+jitter+1]
    if curWaveformPiece.size==0:
        return 0,0,0,0
#    curWaveformPiece = data[:, timepoint-jitter:timepoint+jitter+1]
    # print(timepoint, before, after, curWaveformPiece.size)
    mpeak = np.max(curWaveformPiece, axis=1)
    
    # print(curWaveformPiece.shape, mpeak.shape)

    curWaveformPiece = fullWaveformPiece[:, :before+jitter+1]    
#    curWaveformPiece = data[:, timepoint-before:timepoint+jitter+1]
    prevalleyPos = np.argmin(curWaveformPiece, axis=1)
    prevalleyPosMode = stats.mode(prevalleyPos)[0][0]
    # print(prevalleyPos, prevalleyPosMode, curWaveformPiece.shape, curWaveformPiece[:, prevalleyPosMode-2:prevalleyPosMode+3].shape)
    
    prevalley = np.min(curWaveformPiece[:, ((prevalleyPosMode-jitter)*((prevalleyPosMode-jitter)>0)):prevalleyPosMode+3], axis=1)
    # print(prevalleyPos, prevalleyPosMode, curWaveformPiece.shape, curWaveformPiece[:, prevalleyPosMode-2:prevalleyPosMode+3].shape, prevalley.shape)

    curWaveformPiece = fullWaveformPiece[:, before:]
#    curWaveformPiece = data[:, timepoint:timepoint+after]
    postvalleyPos = np.argmin(curWaveformPiece, axis=1)
    postvalleyPosMode = stats.mode(postvalleyPos)[0][0]
    postvalley = np.min(curWaveformPiece[:, ((postvalleyPosMode-jitter)*((postvalleyPosMode-jitter)>0)):postvalleyPosMode+3], axis=1)
    
    # print(curWaveformPiece.shape, postvalley.shape)

    curWaveformPiece = fullWaveformPiece
#    curWaveformPiece = data[:, timepoint-before:timepoint+after]
    energy = np.sqrt(np.sum(np.square(curWaveformPiece), axis=1))

    del fullWaveformPiece
    
    return mpeak, prevalley, postvalley, energy
    

print("making raw waveform file...")
outputRawWaveformFile = np.memmap(path+"\\parms_"+shank+".waveforms", 'int16', 'w+', shape=(len(newPeakTimepoints), numChannels, before+after))
print('done')

ts = np.load(path+"\\timestampsCSC_"+shank+".npy")
spikeValues['ts'] = ts[newPeakTimepoints]
spikeValues['SpikeID'] = np.arange(len(newPeakTimepoints))
#print(spikeValues['ts'][0], spikeValues['ts'][-1])
#ts = sampleCSC['ts']
#for i in range(len(ts)):
#    print(ts[i], i)
#sys.exit()
spikeValues['tsSec'] = ts[newPeakTimepoints]/1000000

for timepointIdx in range(len(newPeakTimepoints)):
#    if timepointIdx>100000:
#        break
    timepoint = newPeakTimepoints[timepointIdx]
    if (timepointIdx%10000)==0:
        print(timepointIdx*100/len(newPeakTimepoints));
    mpeak, prevalley, postvalley, energy = calculateParams(timepointIdx, timepoint, channelData, before, after)
    spikeValues[timepointIdx]['MPeak'] = mpeak
    spikeValues[timepointIdx]['PreValley'] = prevalley
    spikeValues[timepointIdx]['PostValley'] = postvalley
    spikeValues[timepointIdx]['Energy'] = energy
    
    # print(spikeValues[timepoint])
    
    
#    waveform = channelData[:,timepoint-before:timepoint+after]
#    print(waveform.shape)
    # break
     
outputFile = open(path+"\\parms_"+shank+".Ntt.parms", 'w')

outputParmsType = np.dtype([
        ('ts', '<u8'),
        ('MPeak', '<f4', (numChannels)),
        ('PreValley', '<f4', (numChannels)),
        ('SpikeID', '<f4'),
        ('Energy', '<f4', (numChannels)),
        ('MaxHeight', '<f4'),
        ('MaxWidth', '<f4'),
        ('PosX', '<f4'),
        ('PosY', '<f4'),
        ('tsSec', '<f4'),
        ('PostValley', '<f4', (numChannels))
    ])

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

# outputFile.write(spikeValues.tobytes())
spikeValues.tofile(outputFile)

outputFile.close();

#for i in range(len(newPeakTimepoints)):
##    cscFiles[]
#    spikeValues['MPeak'][i]
#    spikeValues['PreValley'][i]
#    spikeValues['Energy'][i]
#    spikeValues['Valley'][i]
#        


# for timepointIdx in range(len(peakTimepoints)):
    # if peakTimepointsDiff[timepointIdx]>1:
        # newPeakTimepoints.append(peakTimepoints[timepointIdx])



#if not os.path.exists(path+"\\allData.npy"):
#    fileData = []
#    for file in peakTimepointsFileList:
#        print("loading "+file)
#        fileData.append(np.load(file[:-3]+"npz", mmap_mode=True)['data'])
#    np.save(path+"\\allData", fileData)
#    del(fileData)    
#
#fileData = np.load(path+"\\allData.npy", mmap_mode='r')x