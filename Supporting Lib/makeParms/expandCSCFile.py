# -*- coding: utf-8 -*-
"""
Created on Sat Aug 24 21:15:27 2019

@author: vyash
"""

import sys
import numpy as np
#sys.path.append("D:\\code\\baseFuncs")
import fileLoader
import os

if(len(sys.argv)==2):
    pathFolder = sys.argv[1].split("\\")[-1].split("_")
    curShank = pathFolder[0]
    curThresh = pathFolder[1]
    print("current shank: ", curShank, ", current threshold: ", curThresh)
    # curShank = input("current shank: ")
    # curThresh = input("threshold: ")
else:
    curShank = sys.argv[2]
    curThresh = sys.argv[3]

inputFileList = np.load(sys.argv[1]+"\\peakTimepointsInputFileList_"+curShank+"_"+curThresh+".npy")
outputFileList = np.load(sys.argv[1]+"\\peakTimepointsOutputFileList_"+curShank+"_"+curThresh+".npy")

ncsType = np.dtype([
    ('ts', '<u8'),
    ('channelNum', '<u4'),
    ('sampleFreq', '<u4'),
    ('numValidSamples', '<u4'),
    ('samples', '<i2', (512, ))
])

_, header = fileLoader.load_NCS(inputFileList[0], count=1)
splitHeader = header.split("\n")[:-1]
adBitVolts = 0
for line in splitHeader:
    if "-ADBitVolts " in line:
        adBitVolts = float(line.split(" ")[-1])
adBitVolts *= 1000000 #convert it to microvolts

prevTS = np.empty(0)
allDataOutputFile = 0;
dataFileName = sys.argv[1]+"\\expandedCSC_"+curShank+".memmap"

dataFileExists = os.path.exists(dataFileName)

for fileIdx in range(len(inputFileList)):
    inputFileHandle = open(inputFileList[fileIdx], mode='r')
    inputFileHandle.seek((16*1024))
    print(inputFileHandle)
    curFile = np.fromfile(inputFileHandle, dtype=ncsType)
    curData = np.array(curFile['samples'].reshape(512*len(curFile)))
    curTS = np.array([curFile['ts']])

    if fileIdx == 0 and not dataFileExists:
        print("making blank output file")
        # outputDataTemp = np.empty((len(inputFileList), len(curData)))
        # np.save(dataFileName, outputDataTemp)
        # del(outputDataTemp)
        # allDataOutputFile = np.load(dataFileName, mmap_mode='r+')
        tempFile = open(dataFileName, 'w')
        tempFile.close()
        allDataOutputFile = np.memmap(dataFileName, dtype='float64', mode='w+', shape=(len(inputFileList), len(curData)))

    if(np.sum(prevTS!=curTS)>0 and fileIdx!=0):
        print("timestamps mismatched", inputFileList[fileIdx])
        print(prevTS, curTS, len(prevTS), len(curTS))
        continue
    prevTS = curTS
    interpolSum = np.array(list(range(512)))*(16000/512)
    interpolatedTS = curTS.T + interpolSum
    interpolatedTS = interpolatedTS.flatten().astype('u8')
    curDataMicroVolts = curData*adBitVolts #convert all data to microvolts
    # np.save(outputFileList[fileIdx][:-4]+"_data.npy", curDataMicroVolts)
    if not dataFileExists:
        allDataOutputFile[fileIdx] = curDataMicroVolts
    del(curDataMicroVolts)
    # print(fileIdx)
    if fileIdx==0:
        np.save("\\".join(outputFileList[0].split("\\")[:-1])+"\\timestampsCSC_"+curShank+".npy", interpolatedTS)    
    del(interpolatedTS)
    if dataFileExists:
        break
    
