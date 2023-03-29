# Knierim_Lab_Neuropixels_Pipeline-2.0

GUI interface to run through following steps in the Manual Spike Sorting pipeline for Neuropixels 1.0 and 2.0. A couple of notes, 1) The path you're going to pick is either in example format 1) C:\animal#\experiment# or 2) C:\animal#\experiment#\imecrecording#_g0._ 2) this program will overwrite previously generated catgt and detect merge peaks _peaks.mat_ files. 3) You will need to configure individual functions to suit your needs, see "EDIT" sections in each function. This step will not take long, you will simply need to define paths to your CatGT, TPrime software, as well as specialize variables used in each.

1. CatGT
2. TPrime
3. Stimulation Artifact Removal
4. Shank Coordinates Generator
5. Detect Peaks
6. Calculate Parms for Winclust

Update Mar. 29th 2023: Do not use the calcparms function yet. It only has capabilities for the Neuropixels 2.0 and is not user friendly.
