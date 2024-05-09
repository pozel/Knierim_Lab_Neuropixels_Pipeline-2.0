# Knierim_Lab_Neuropixels_Pipeline-2.0

A complete walkthrough to get setup with the Neuropixels 2.0 data processing pipeline we use in the Knierim Lab to go from raw .bin data to .parms files for Winclust manual sorting. Use the master script runall_Pipeline2 to run the following steps together:

Step 1
Once you've set up the iMEC recording system along with SpikeGLX software following instructions from the SpikeGLX Git Repo, https://billkarsh.github.io/SpikeGLX/, you can begin recording .bin raw files.

These .bin files can be preprocessed using two SpikeGLX programs called CatGT and TPrime. The goal here is to separate out neural data via bandpassing (600-6000 Hz), global common average referencing, and extracting camera/behavioral data from your ni.bin file. After using CatGT, you can use TPrime to align the timestamps of your camera recordings to the neural timeframe. Details on these processes can be found at the SpikeGLX repo OR their respective ReadMe.html files post-download.

runall_CatGT can be adapted for you own filenaming convention to run a batch of .bin files through CatGT. The goal of these "superscripts" is to remove user input and automate the preprocesing pipeline for a batch of many recordings. This process can be tedious if working on individual files. Similarly, runall_TPrime can be adapted for your needs to run all your data files (ni.bin) through TPrime.

A couple of notes when customizing your scripts, 1) The raw data file path you're going to pick is either in example format 1) C:\animal#\experiment# for batch recordings, with individual recordings within your experiment# folder or 2) C:\animal#\experiment#\imecrecording#_g0._ for individual recordings. 2) this program will overwrite previously generated CatGT and TPrime files. 3) You will need to configure individual functions to suit your needs, see "EDIT" sections in each function. This step will not take long, you will simply need to define paths to your CatGT, TPrime software, as well as specialize variables used in each.

Step 2
You will need to create a mapping of your shank coordinates via superscript runall_Coords for later steps in spike extraction (e.g., spatial and temporal filtering). This file calls on "SGLXMetaToCoords," adapted from the SpikeGLX team to obtain the meta file information to generate a set of site coordinates.

Step 3
Detect Peaks will be the step to extract spikes taken from JRCLUST spike extraction methods. See runall_DetectPeaks. Steps include finding and merging peaks with a spatiotemporal filter at your desired uV threshold cutoff. Here, you'll have to set your probe type (if using another type of probe from the NP 2.0 v2023), select channels to exclude (noisy channels) and finally check the uVPerBit value since this is varied across probe type.

Step 4
Calculates the output .Parms for Winclust from extracted spikes. See runall_CalcParms. This program calls upon a python script called catGT_to_parms_merged.py to 1) generate the waveform file, 2) calculate site distances, and 3) create your parms file for Winclust. You can only extract 32 channels at a time, constrained by Winclust. You can define your channel mapping using a .csv file of 32 channels. See the template under "channel_template" included here as this will cause errors if the mapping is off.

Step 5
Csv2pos to get .pos files for clustering. Relatively similar to csv2pos for other applications, however uses NP information to populate the header.


