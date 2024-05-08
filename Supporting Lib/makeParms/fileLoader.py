# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 01:59:27 2017

@author: vyash
"""

import numpy as np

#file loaders for various file types



#----------------Load cl-maze----------------#
def load_clmaze(filename, usecols=None, correctResolution=False):
    """
    Load data from WinClust output "cl-maze[S].[C]" files,
    where [S] is the session number and [C] is the cluster number

    Parameters
    ----------
    filename: str
        The full path of the file
    usecols: sequence, optional
        Array of index values designating the columns to output
    correctResolution: bool, optional
        Corrects the X-axis resolution issue found in Cheetah 5.x., where the 
        frame resolution is saved as 720x480 instead of 640x480. Effectively, 
        this function multiplies the X axis values by 64/72.

    Returns
    -------
    data : ndarray
        Data read from the file.

    File Column Definitions
    -----------------------    
    SpikeID, PeakX, PeakY, PeakA, PeakB, PreVallayX, PreValleyY, PreValleyA, 
    PreValleyB, EnergyX, EnergyY, EnergyA, EnergyB, MaxHeight, MaxWidth, 
    XPos, YPos, Timestamp
    
    """
    names = np.array(["SpikeID", "PeakX", "PeakY", "PeakA", "PeakB", "PreVallayX", \
    "PreValleyY", "PreValleyA", "PreValleyB", "EnergyX", "EnergyY", \
    "EnergyA", "EnergyB", "MaxHeight", "MaxWidth", "XPos", "YPos", "Timestamp"])
    data = np.loadtxt(filename, delimiter=',', skiprows=13, usecols=usecols, dtype=np.float64)
    
    if len(data.shape)==0:
        return None
    if data.shape[0]==0:
        return None
    
    if correctResolution:
        if usecols is None:
            data[:,-3]*=(64/72)
        elif "XPos" in names[usecols]:
            ind = np.where(names[usecols]=="XPos")
            data[:,ind]*=(64/72)
    return data

#-----------------------------------------------------------------------------#



#----------------Load Pos.p.ascii----------------#
def load_Occupancy(filename, usecols=None, correctResolution=False):
    """
    Load data from CalcParms output "Pos.p.ascii" files
    
    Parameters
    ----------
    filename: str
        The full path of the file
    usecols: sequence, optional
        Array of index values designating the columns to output
    correctResolution: bool, optional
        Corrects the X-axis resolution issue found in Cheetah 5.x., where the 
        frame resolution is saved as 720x480 instead of 640x480. Effectively, 
        this function multiplies the X axis values by 64/72.
        
    Returns
    -------
    data : ndarray
        Data read from the file.

    File Column Definitions
    -----------------------    
    Timestamp, XPos, YPos, HeadDirection
    
    """
    names = np.array(["Timestamp", "XPos", "YPos", "HeadDirection"])
    data = np.loadtxt(filename, delimiter=',', skiprows=24, usecols=usecols, dtype=np.float64)
    if correctResolution:
        if usecols is None:
            data[:,-3]*=(64/72)
        elif "XPos" in names[usecols]:
            ind = np.where(names[usecols]=="XPos")
            data[:,ind]*=(64/72)
    return data

#-----------------------------------------------------------------------------#


    
#----------------Load Defaults----------------#
def load_Defaults(filename):
    """
    Load data from WinClust output "Defaults" files,
    for the purpose of attaining epoch boundaries

    Parameters
    ----------
    filename: str
        The full path of the file
    
    Returns
    -------
    epochs : dictionary
        Keys contain the epoch name, values contain the timestamp bounds.

    """

    epochs = {}
    with open(filename) as file:
        for line in file:
            if '"Epoch"' in line:
                line = line.split(',')[1][1:-1].split(' ')
                line = [x for x in line if x is not '']
                if line[-1] == '"':
                    line = line[:-1]
                else:
                    line[-1] = line[-1][:-1]
                epochs[line[0][:-1]]=(int(line[1]), int(line[2]))
    return epochs

#-----------------------------------------------------------------------------#

#----------------Load Defaults----------------#
def load_Notes(filename):
    """
    Load data from WinClust output "ClNotes" files, for the purpose of reading 
    cluster ratings. Ratings of "poor" are designated as "1", and ratings of 
    "good" are designated as "5". Missing ratings are designated as "-1"

    Parameters
    ----------
    filename: str
        The full path of the file
    
    Returns
    -------
    ratings : list
        List of all clusters with ratings. The size of the list depends on the
        number of clusters that have been rated in the ClNotes file.
        Cluster Number = Index of Rating List + 1
    notes : List
        List representing the notes for each cluster. Indexing is the same as 
        the ratings list above.

    """
    
    ratingValues = ['Poor', 'Marginal', 'Fair', 'Pretty Good', 'Good']

    ratings = []
    notes = []
    with open(filename) as file:
        for line in file:
            if ',"",""' in line:
                continue
            line = line.strip().split(',')
            try:
                ratings.append(ratingValues.index(line[1][1:-1])+1)
            except ValueError:
                ratings.append(-1)
            notes.append(line[2][1:-1])
    return ratings, notes

#-----------------------------------------------------------------------------#

#----------------Load NVT----------------#
nvtType = np.dtype([
    ('trash1', '<u2', (3, )),
    ('ts', '<u8'),
    ('Points', '<u4', (400, )),
    ('trash2', '<i2'),
    ('estimation', '<i4', (3, )),
    ('targets', '<i4', (50, ))
])

def load_NVT(filename, count=-1, headerRaw=False):
    """
    Load Neuralynx NVT file

    Parameters
    ----------
    filename: str
        The full path of the file
    count: integer
        Number of instances to load
    
    Returns
    -------
    nvt : Numpy array
        Numpy array using the nvtType dtype

    """
    if headerRaw:
        nvtFile = open(filename, 'rb')
        header = nvtFile.read(16*1024)
        nvtFile.close()
    else:
        nvtFile = open(filename, 'r', encoding='mbcs')
        header = nvtFile.read(16*1024)
        nvtFile.close()
    nvtFile = open(filename, 'rb')
    nvtFile.seek(16*1024) #skip header
    return np.fromfile(nvtFile, dtype=nvtType, count=count), header
    
#-----------------------------------------------------------------------------#

#----------------Load NTT----------------#
nttType = np.dtype([
    ('ts', '<u8'),
    ('spikeEntryNumber', '<u4'),
    ('cellNumber', '<u4'),
    ('parameters', '<u4', (8)),
    ('samples', '<i2', (32,4))
])

def load_NTT(filename, count=-1, headerRaw=False):
    """
    Load Neuralynx NTT file

    Parameters
    ----------
    filename: str
        The full path of the file
    count: integer
        Number of instances to load
    
    Returns
    -------
    ntt : Numpy array
        Numpy array using the nvtType dtype

    """
    if headerRaw:
        nttFile = open(filename, 'rb')
        header = nttFile.read(16*1024)
        nttFile.close()
    else:
        nttFile = open(filename, 'r', encoding='mbcs')
        header = nttFile.read(16*1024)
        nttFile.close()
    nttFile = open(filename, 'rb')
    nttFile.seek(16*1024) #skip header
    return np.fromfile(nttFile, dtype=nttType, count=count), header
    
#-----------------------------------------------------------------------------#

#----------------Load NCS----------------#
ncsType = np.dtype([
    ('ts', '<u8'),
    ('channelNum', '<u4'),
    ('sampleFreq', '<u4'),
    ('numValidSamples', '<u4'),
    ('samples', '<i2', (512, ))
])

def load_NCS(filename, count=-1, headerRaw=False):
    """
    Load Neuralynx NCS file

    Parameters
    ----------
    filename: str
        The full path of the file
    count: integer
        Number of instances to load
    
    Returns
    -------
    ncs : Numpy array
        Numpy array using the nvtType dtype

    """
    if headerRaw:
        ncsFile = open(filename, 'rb')
        header = ncsFile.read(16*1024)
        ncsFile.close()
    else:
        ncsFile = open(filename, 'r', encoding='mbcs')
        header = ncsFile.read(16*1024)
        ncsFile.close()
    ncsFile = open(filename, 'rb')
    ncsFile.seek(16*1024) #skip header
    return np.fromfile(ncsFile, dtype=ncsType, count=count), header
    
#-----------------------------------------------------------------------------#

#----------------Load NEV----------------#
def load_NEV(filename):
    """
    Load Neuralynx NEV file

    Parameters
    ----------
    filename: str
        The full path of the file
    
    Returns
    -------
    nev : Numpy array
        Numpy array using the nevType dtype

    """
    
    nevType = np.dtype([
        ('trash1', '<i2', (3, )),
        ('ts', '<u8'),
        ('eventID', '<i2'),
        ('TTL', '<i2'),
        ('trash2', '<i2', (3, )),
        ('dnExtra', '<i4', (8, )),
        ('string', '<S128')
    ])
    
    nevFile = open(filename)
    nevFile.seek(16*1024) #skip header
    return np.fromfile(nevFile, dtype=nevType)
    
#-----------------------------------------------------------------------------#