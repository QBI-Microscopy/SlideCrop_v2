import numpy as np
import h5py
import matplotlib
import os
from math import ceil

from scipy import ndimage
import timeit as T
"""
General Page to store Ideas and methods to improve performance of SlideCrop backEnd. 

Main Problem is the cropping of all planes after segmentation
.IMS file has high degree of subdividing image data (files for each channel, resolution and timepoint
chunking to include ndarray of (time, channel, x,y,z) could improve read and crop performance
Chunking can improve data read costs by storing data in (xsize, ysize, zsize) chunks
Must consider chunk cache when designing chunk params as to allow chunks to be effective. 

General case for .IMS is that z and time dimensions are only 1 and 3 channels
Alot of ram access between for tiff files and storing alot of the datasets on RAM

- Check whether .IMS -> .hdf uses the one image array for different paths (i.e multichannel image with separate paths
  to each channel, analagous for time component)

- h5py (and assumably hdf) can use compression filters but de/compression is performed automatically on I/O read/write 
  making there no RAM benefits from this action. Tradeoff is solely Disk Storage <-> I/O R/W speed (from primitive testing 8 times slowing reading in file)

"""

#  TODO: Test time requirements to transform .ims file to (x,y,c) data set arrays to improve performance
#  TODO: Work on compression ideas and operating on compressed h5py files

FILECOUNT = 1
FILEPATH = "C:/Users/uqjeadi2/Downloads/NG_GAD67_GFP16-B.ims"
STOREFILEPATH = "C:/Users/uqjeadi2/Downloads/"
def import_hdf_File():
    return h5py.File(FILEPATH)

