# -*- coding: utf-8 -*-
"""
Created on Sat Aug 24 18:57:37 2019

@author: vyash
"""

import numpy as np
import os
import sys
import importlib
from multiprocessing import Pool, current_process
from scipy import signal
from fileLoader import load_NCS

ncsType = np.dtype([
    ('ts', '<u8'),
    ('channelNum', '<u4'),
    ('sampleFreq', '<u4'),
    ('numValidSamples', '<u4'),
    ('samples', '<i2', (512, ))
])

def getSignalPeaks(inputFilename, threshValue, adBitVolts, outputFilePath):
    print(current_process().name, inputFilename, outputFilePath)
    if os.path.exists(outputFilePath):
        return
    
    inputFileHandle = open(inputFilename, mode='r')
    inputFileHandle.seek((16*1024))
    curFile = np.fromfile(inputFileHandle, dtype=ncsType)
    curData = np.array(curFile['samples'].reshape(512*len(curFile)))
    curTS = np.array([curFile['ts']])
    interpolSum = np.array(list(range(512)))*(16000/512)
    interpolatedTS = curTS.T + interpolSum
    interpolatedTS = interpolatedTS.flatten().astype('u8')
    curDataMicroVolts = curData*adBitVolts #convert all data to microvolts
#    print(curData[:10], curDataMicroVolts[:10], adBitVolts)
    
    curDataMask = curDataMicroVolts>threshValue #apply thresholding
    
    starts = np.where(curDataMask[:-1]<curDataMask[1:])[0]+1
    ends = np.where(curDataMask[:-1]>curDataMask[1:])[0]+1
    
    if len(ends)!=len(starts):
        print(current_process().name, "mismatched chunk starts/ends\tstarts: ", len(starts), "\tends: ", len(ends))
        print(current_process().name, starts[:10], ends[:10])
    if len(ends)<len(starts):
        print(current_process().name, "correcting ends by adding max value to the end")
        ends = np.append(ends, len(curDataMask))
    if len(starts)<len(ends):
        print(current_process().name, "correcting starts by adding 0 to the beginning")
        starts = np.insert(starts, 0, 0)
        
    print(current_process().name, "finding peaks")
    
    peaks, _ = signal.find_peaks(curDataMicroVolts, height=threshValue)
    
    confidentPeaks = np.ones_like(peaks, dtype=bool)
    
    # if "CSC_B13" in inputFilename:
    #     peaks = []
    #     confidentPeaks = []
    
    
#    for i in range(len(starts)):
#        curPeaks = np.argwhere((peaks>=starts[i])*(peaks<ends[i]))
#        if len(curPeaks)>1:
##            print(curDataMicroVolts[peaks[curPeaks]], np.argmax(curDataMicroVolts[peaks[curPeaks]]), peaks[curPeaks])
#            curPeaks = np.delete(curPeaks, np.argmax(curDataMicroVolts[peaks[curPeaks]]))
#            confidentPeaks[curPeaks] = False
    
    print(current_process().name, "writing file")
    
#    np.save(outputFilePath+"data.npy", curDataMicroVolts)
#    np.save(outputFilePath+"ts.npy", interpolatedTS)
    np.savez_compressed(outputFilePath, peaks = peaks, confidentPeaks = confidentPeaks)
#    np.savez_compressed(outputFilePath, data = curDataMicroVolts, ts = interpolatedTS, peaks = peaks, confidentPeaks = confidentPeaks)


if __name__ == '__main__':
    
    pool = Pool(processes=4)

    if(len(sys.argv)==2):
        enabledShanks = input("current shank: ")
        numChannels = int(input("numChannels: "))
        threshold = int(input("threshold: "))
    else:        
        enabledShanks = sys.argv[2]
        numChannels = int(sys.argv[3])
        threshold = int(sys.argv[4])
    
    def getInputFilenames():
        availableFiles = []
        for shank in enabledShanks:
            for site in range(1,numChannels+1):
                testPath = sys.argv[1]+"\\CSC_"+shank+str(site)+".ncs"
                if os.path.exists(testPath):
                    availableFiles.append(testPath)
        return availableFiles
    
    availableFiles = getInputFilenames()
#    numChannels = len(availableFiles)
    
    
    _, header = load_NCS(availableFiles[0], count=1)
    splitHeader = header.split("\n")[:-1]
    adBitVolts = 0
    for line in splitHeader:
        if "-ADBitVolts " in line:
            adBitVolts = float(line.split(" ")[-1])
    adBitVolts *= 1000000 #convert it to microvolts

    print(threshold, adBitVolts)
#    np.save(sys.argv[2]+"\\peakTimepointsFileList_"+enabledShanks, availableFiles)
    
    outPath = sys.argv[1]+"\\"+enabledShanks+"_"+str(threshold)+"\\"
    
    if not os.path.exists(outPath):
        os.mkdir(outPath)
    outputFilenames = [outPath+"\\"+availableFiles[idx].split("\\")[-1][:-4]+"_"+str(threshold)+".npz" for idx in range(len(availableFiles))]
    print(outputFilenames)
    np.save(outPath+"\\peakTimepointsOutputFileList_"+enabledShanks+"_"+str(threshold), outputFilenames)
    np.save(outPath+"\\peakTimepointsInputFileList_"+enabledShanks+"_"+str(threshold), availableFiles)

    mapArguments = [[availableFiles[idx], threshold, adBitVolts, outputFilenames[idx]] for idx in range(len(availableFiles))]
    for x in mapArguments:
        print(x)
    
    print('pool start')
    print(mapArguments)
    pool.starmap(getSignalPeaks, mapArguments)
    pool.close()
    pool.join()


    availableFiles = outputFilenames
    
    allPeaks = []
    allConfidentPeaks = []
    
    for idx in range(len(availableFiles)):
        curFile = np.load(availableFiles[idx])
    #    f2 = np.load(sys.argv[1]+"\\"+availableFiles[idx+1].split("\\")[-1][:-4]+".npz")
        allPeaks.append(curFile['peaks'])
        allConfidentPeaks.append(curFile['confidentPeaks'])
        print(len(allPeaks[idx]))
    #
    #print(len(reduce(np.intersect1d, [allPeaks[i][allConfidentPeaks[i]] for i in range(5)])))
    allPeaksFlat = np.array([x for channelPeaks in allPeaks for x in channelPeaks])
    allConfidentPeaksFlat = np.array([x for channelPeaks in allConfidentPeaks for x in channelPeaks])
    
    uniquePeakTimepoints, uniqueCounts = np.unique(allPeaksFlat[allConfidentPeaksFlat], return_counts = True)
    
    print("Pre-filtered length: ", len(uniquePeakTimepoints))
    
    filteredIdx = [0]
    curPeakTS = uniquePeakTimepoints[0]
    for idx in range(1, len(uniquePeakTimepoints)):
        curDiff = uniquePeakTimepoints[idx]-curPeakTS
        if curDiff>32:
            filteredIdx.append(idx)
            curPeakTS = uniquePeakTimepoints[idx]
    
    ##ENABLE THESE FOLLOWING LINES TO ENABLE FILTERING TO PREVENT RE-TRIGGERING
    uniquePeakTimepoints = uniquePeakTimepoints[filteredIdx]
    print("Post-filtered length: ", len(uniquePeakTimepoints))
    
    
#    print(np.unique(np.diff(uniquePeakTimepoints), return_counts=True))
            
    
    np.save(outPath+"\\peakTimepoints_"+enabledShanks+"_"+str(threshold), uniquePeakTimepoints)
    
#
#
#for idx in range(0, 8, -1):
##for idx in range(numChannels):
##for idx in [int(sys.argv[3])]:
#    if os.path.exists(sys.argv[1]+"\\"+availableFiles[idx].split("\\")[-1][:-4]+"_"+str(threshold)+".npz"):
#        continue
#    print(inputFileHandles[idx])
#    data, ts, peaks, confidentPeaks = getSignalPeaks(inputFileHandles[idx], threshold, adBitVolts)
#    
