# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 22:32:32 2021

@author: vyash
"""

import numpy as np
import sys
import math

numChannels = 32
parmsPath = sys.argv[1]
pospPath = sys.argv[2]

parmsType = np.dtype([
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


parmsHandle = open(parmsPath, 'rb')
header = []
for line in parmsHandle:
    header.append(line)
    if b"%%ENDHEADER" in line:
        break
        
parmsFile = np.fromfile(parmsHandle, dtype=parmsType)

pospFile = np.genfromtxt(pospPath, delimiter=",", comments='%', dtype=np.dtype([('ts','u8'), ('PosX', 'f4'), ('PosY', 'f4'), ('HD', 'f4')]))
# idx = np.searchsorted(pospFile['ts'], parmsFile['ts'], side='left')
# print(idx, len(pospFile))
# pospParmsTS = pospFile['ts'][idx]
# print(pospParmsTS-parmsFile['ts'])

newX = np.zeros_like(parmsFile['PosX'])
newY = np.zeros_like(parmsFile['PosX'])

maskWithinRange = (parmsFile['ts']>=pospFile['ts'][0]) * (parmsFile['ts']<=pospFile['ts'][-1])

newX[np.invert(maskWithinRange)] = -99
newY[np.invert(maskWithinRange)] = -99

newX[maskWithinRange] = np.interp(parmsFile['ts'][maskWithinRange], pospFile['ts'], pospFile['PosX'])
newY[maskWithinRange] = np.interp(parmsFile['ts'][maskWithinRange], pospFile['ts'], pospFile['PosY'])

parmsFile['PosX'] = newX
parmsFile['PosY'] = newY

newParms = open(parmsPath[:-10]+"_withPos.Ntt.parms", 'wb')
for line in header:
    newParms.write(line)
parmsFile.tofile(newParms)
newParms.close()