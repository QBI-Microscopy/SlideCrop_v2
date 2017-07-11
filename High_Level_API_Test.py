"""
    Script to compare and test the memory and time efficiency of the low and high APIs for HDF and h5py. Following
    features are tested as they are the most common use in SlideCropper:
        - Opening, loading and closing files from Disk
        - Opening subslices into RAM and manipulating datasets
        - Creating new HDF and TIFF files, filling datasets from .IMS files
        - Iterating through file groups and performing operations on the data.
"""

import h5py
import numpy as np
import random
import memory_profiler

FILEDIRECTORY = "E:/"
MAINFILEPATH = FILEDIRECTORY + "trial.hdf"
EXISTING_FILE = "C:/Users/uqjeadi2/Downloads/NG_GAD67_GFP16-B.ims"

@profile
def opening_and_creating_files():
    # Open existing File
    exisiting_file = h5py.File(EXISTING_FILE)


    # Save into new directory
    exisiting_file.copy(exisiting_file, MAINFILEPATH)
    new_file = h5py.File(MAINFILEPATH)

    #Close First
    new_file.close()
    #Close Second
    exisiting_file.close()
    pass

def create_dataset():
    # Create standard, random dataset
    # float dataset
    # Create Standard, 2+D dataset

    #Create New Group
    # chunked dataset

    #Create Nested Group
    # Resizeable Dataset
    # Compressed Dataset
    pass

#  Typical operations when performing analysis of IMS file on SlideCrop
def slicing_and_operating_datasets():
    #Slicing 1D data

    #Slicing 2+D dataset

    # Slicing chunked Data

    #Slicing compressed Data

    #Resizing datasets
    pass

#  Typical operations for saving and sending data into .tiff file formats
def tiff_and_ims_operations():
    pass

#  Typical operations when iterating over grouped datasets in IMS
def groups_iteration():
    pass

# Typical operations when cropping in SlideCrop application
def cropping_IMS_to_hdf():
    pass

@profile
def my_func():
    a = h5py.File(FILEDIRECTORY + str(random.getrandbits(10))+ "hdf5")



if __name__ == '__main__':
    opening_and_creating_files()
    create_dataset()
    slicing_and_operating_datasets()
    tiff_and_ims_operations()
    groups_iteration()
    cropping_IMS_to_hdf()