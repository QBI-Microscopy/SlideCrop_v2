import numpy as np
import h5py
import matplotlib
import os
from math import ceil
#from scipy import ndimage
from timeit import timeit
"""
General Page to store Ideas and methods to improve performance of SlideCrop backEnd. 

Main Problem is the cropping of all planes after segmentation
.IMS file has high degree of subdividing image data (files for each channel, resolution and timepoint
chunking to include ndarray of (time, channel, x,y,z) could improve read and crop performance
Chunking can improve data read costs by storing data in (xsize, ysize, zsize) chunks
Must consider chunk cache when designing chunk params as to allow chunks to be effective. 

General case for .IMS is that z and time dimensions are only 1 and 3 channels
Alot of ram access between for tiff files and storing alot of the datasets on RAM


"""

#  TODO: Test time requirements to transform .ims file to (x,y,c) data set arrays to improve performance
#  TODO: Work on compression ideas and operating on compressed h5py files


FILEPATH = "C:/Users/uqjeadi2/Downloads/NG_GAD67_GFP16-B.ims"

def import_hdf_File():
    return h5py.File(FILEPATH)

def hdf_data_from_Resolution(resLev, h5py, chan=None):
    if not chan:
        return h5py["DataSet/ResolutionLevel " + str(resLev) + "/TimePoint 0/Channel 0/Data"]

    return h5py["DataSet/ResolutionLevel " + str(resLev) + "/TimePoint 0/Channel " + str(chan) + "/Data"]

def main():
    print(timeit(import_hdf_File))
    file = import_hdf_File()
    # print("channel 0" + str(timeit(hdf_data_from_Resolution(0, file))))
    # print("channel 1" + str(timeit(hdf_data_from_Resolution(1, file))))
    # print("channel 2" + str(timeit(hdf_data_from_Resolution(2, file))))
    # print("channel 3" + str(timeit(hdf_data_from_Resolution(3, file))))
    # print("channel 4" + str(timeit(hdf_data_from_Resolution(4, file))))
    # print("channel 5" + str(timeit(hdf_data_from_Resolution(5, file))))

if __name__ == '__main__':
    main()