1. SGLXMetaToCoords.m - this extracts the meta file information to generate a set of site coordinates
2. detect_merge_peaks.m - this finds and merges peaks with the spatiotemporal filter. Set the probe type, select channels to exclude, set your thresh
3. catGT_to_parms_merged.py

1) get the physical coordinates of each channel to create a "map" of channel locations
2) using jrclust, find spike events that pass a 50 uV threshold in batches of data
3) look for duplicate peaks in a 50 um spatial range and 7 samples in time range
4) merge any duplicate peaks that are idenitfied by the spatialtemporal filter
5) identify peaks in "jitter" range
6) write peaks to winclust format and remove spikes from peaks view, but not waveform view