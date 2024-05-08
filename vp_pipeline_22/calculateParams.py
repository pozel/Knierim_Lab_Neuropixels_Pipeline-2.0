import numpy as np
from scipy.stats import stats #this function was a part of catGT_to_parms_merged in VP's version
def calculateParams(taskIndex):#, fullWaveformPieceInput):
    fullWaveformPiece = outputRawWaveformFile[taskIndex, :, :]*tiledConversionFactors
    peakLocation = sites[taskIndex]
    output = [[0]*len(fullWaveformPiece)]*4
    # output[-1] = [taskIndex]*len(fullWaveformPiece)
    curWaveformPiece = fullWaveformPiece[:, before-jitter:before+jitter+1]
    if curWaveformPiece.size==0:
        return taskIndex, 0,0,0,0
    output[0] = np.max(curWaveformPiece, axis=1)
    #applying spatial mask for peak calculation
    output[0] *= nearbySites[nearbySites[:,0]==peakLocation, 1:][0]    
    curWaveformPiece = fullWaveformPiece[:, :before+jitter+1]    
    prevalleyPos = np.argmin(curWaveformPiece, axis=1)
    prevalleyPosMode = stats.mode(prevalleyPos)[0][0]
    output[1] = np.min(curWaveformPiece[:, ((prevalleyPosMode-jitter)*((prevalleyPosMode-jitter)>0)):prevalleyPosMode+3], axis=1)
    ##******SOMETHING IS WRONG HERE FOR POSTVALLEY CALCULATION, MEMORY CONFLICT?******
    curWaveformPiece = fullWaveformPiece[:, before:]
    postvalleyPos = np.argmin(curWaveformPiece, axis=1)
    postvalleyPosMode = stats.mode(postvalleyPos)[0][0]
    output[2] = np.min(curWaveformPiece[:, ((postvalleyPosMode-jitter)*((postvalleyPosMode-jitter)>0)):postvalleyPosMode+3], axis=1)
    curWaveformPiece = fullWaveformPiece
    output[3] = np.sqrt(np.nansum(np.square(curWaveformPiece), axis=1))
    # return taskIndex, mpeak, prevalley, postvalley, energy
    return output