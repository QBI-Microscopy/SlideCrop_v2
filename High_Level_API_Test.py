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
from  memory_profiler import *
from line_profiler import *
from timeit import Timer


FILEDIRECTORY = "E:/"
MAINFILEPATH = FILEDIRECTORY + "trial.hdf"
EXISTING_FILE = "E:/NG_GAD67_GFP16-B.ims"
USED_PATH = FILEDIRECTORY + "empty" + str(random.getrandbits(10)) # + ".hdf"

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

@profile
def create_dataset():
    file = h5py.File(USED_PATH + str(random.getrandbits(8)) + ".hdf")

    # Create standard, random dataset
    r_set  = np.random.randint(0, 1000, size=(200,200, 200), dtype='i')
    file.create_dataset("standard", (200,200, 200), dtype = 'i', data = r_set)

    # float dataset
    f_set = np.random.rand(200,200, 200)
    file.create_dataset("float", (200,200, 200), dtype='f', data=f_set)

    #Create New Group
    sub = file.create_group("subgroup")
    # chunked dataset
    c_set = np.random.randint(0, 1000, size=(200,200, 200), dtype='i')
    sub.create_dataset("chunked", (200,200, 200), dtype='i', data= c_set, chunks=(10,10,10))

    #Create Nested Group
    nest = sub.create_group("nested")

    # Compressed Dataset
    nest.create_dataset("compressed", (200,200, 200), dtype= 'i', data= r_set, compression="gzip", compression_opts=9)


#  Typical operations when performing analysis of IMS file on SlideCrop
@profile
def slicing_and_operating_datasets():
    file = h5py.File(USED_PATH)

    #Slicing sequential data
    r_set= file.get("standard")
    slicer1 = r_set[0,0,:]
    slicer2 = r_set[0,:,0]
    slicer3 = r_set[:,0,0]
    slicer4 = r_set[[1,2],1:4,1:4]
    slicer5 = r_set[1:4,1:4, [1,2]]

    # Slicing compressed Data
    c_set = file.get("subgroup/nested/compressed")
    slicec1 = c_set[0, 0, :]
    slicec2 = c_set[0, :, 0]
    slicec3 = c_set[:, 0, 0]
    slicec4 = c_set[[1, 2], 1:4, 1:4]
    slicec5 = c_set[1:4, 1:4, [1, 2]]

    #Slicing chunked Data
    ch_set = file.get("subgroup/chunked")
    slicech1 = ch_set[0, 0, :]
    slicech2 = ch_set[0, :, 0]
    slicech3 = ch_set[:, 0, 0]
    slicech4 = ch_set[[1, 2], 1:4, 1:4]
    slicech5 = ch_set[1:4, 1:4, [1, 2]]


#  Typical operations for saving and sending data into .tiff file formats
def tiff_and_ims_operations():
    pass

#  Typical operations when iterating over grouped datasets in IMS
def groups_iteration():
    pass

# Typical operations when cropping in SlideCrop application
def cropping_IMS_to_hdf():
    pass


if __name__ == '__main__':
    print(str(Timer(lambda: create_dataset()).timeit(5)))
    # lp= LineProfiler()
    # lp_wrapper= lp(create_dataset)
    # lp.print_stats()