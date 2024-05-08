# -*- coding: utf-8 -*-
"""
@author: vyash
"""

import glob
import numpy as np
import time
import multiprocessing
import sys
import os.path

inputFilenameBase = sys.argv[1]

ncsType = np.dtype([
    ('ts', '<u8'),
    ('channelNum', '<u4'),
    ('sampleFreq', '<u4'),
    ('numValidSamples', '<u4'),
    ('samples', '<i2', (512, ))
])

fileHandles = []

for shank in "AB":
    for channel in range(32):
        curFilename = inputFilenameBase+"\CSC_"+shank+str(channel+1)+".ncs"
        if os.path.isfile(curFilename):
            fileHandles.append(np.memmap(curFilename, dtype=ncsType, mode='r+', offset=16*1024))
        else:
            print("file missing! " + curFilename)

numRecords = len(fileHandles[0])


def performCAR(recordIdx):
    if recordIdx%int(numRecords/100) == 0:
        print(recordIdx/numRecords)
    tempRecord = np.empty((len(fileHandles), 512), dtype='i2')
    for handleIdx in range(len(fileHandles)):
        tempRecord[handleIdx] = fileHandles[handleIdx][recordIdx]['samples']
    med = np.round(np.median(tempRecord, axis=0)).astype('i2')
    tempRecord-=med
    for handleIdx in range(len(fileHandles)):
        fileHandles[handleIdx][recordIdx]['samples']=tempRecord[handleIdx]    

if __name__ == '__main__':
    #print("WARNING: THIS PROGRAM OVERWRITES EXISTING CSC FILES.")
    #print("DO NOT PROCEED UNLESS YOU HAVE MEANS OF RECOVERING THE ORIGINAL CSC FILES!!!")
    #inVal = ""
    #while(inVal not in ["y", "n"]):
    #    print("Continue? [y/n]")
    #    inVal = input().strip()
    #    if inVal=="n":
    #        sys.exit()
    print("Starting processing...")
    startTime = time.time()
    pool = multiprocessing.Pool(8)
    pool.map(performCAR, range(numRecords))
    for handle in fileHandles:
        del(handle)
    elapsedTime = time.time()-startTime
    print("Finished processing " + str(numRecords) + " records in " + str(elapsedTime) + " seconds")
    print(str(numRecords/elapsedTime) + " records per second")
    
