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
OPER_PATH = FILEDIRECTORY + "empty401235.hdf"
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

#@profile
def create_dataset(path, size):
    F = h5py.File(path)

    # Create standard, random dataset
    r_set  = np.random.randint(0, 1000, size=(size,size, size), dtype='i')
    F.create_dataset("standard", (size,size, size), dtype = 'i', data = r_set)

    # float dataset
    f_set = np.random.rand(size,size, size)
    F.create_dataset("float", (size,size, size), dtype='f', data=f_set)

    #Create New Group
    sub = F.create_group("subgroup")
    # chunked dataset
    c_set = np.random.randint(0, 1000, size=(size,size, size), dtype='i')
    sub.create_dataset("chunked", (size,size, size), dtype='i', data= c_set, chunks=(10,10,10))

    #Create Nested Group
    nest = sub.create_group("nested")

    # Compressed Dataset
    #nest.create_dataset("compressed", (size,size, size), dtype= 'i', data= r_set, compression="gzip", compression_opts=3)
    F.close()

#  Typical operations when performing analysis of IMS file on SlideCrop
@profile
def slicing_and_operating_datasets(PATH):
    file = h5py.File(PATH, "r+")

    #Slicing sequential data
    r_set= file.get("standard")
    slicer1 = r_set[0,0,:]
    slicer2 = r_set[0,:,0]
    slicer3 = r_set[:,0,0]
    slicer4 = r_set[:,1:20,1:20]
    slicer5 = r_set[1:20,1:20, :]

    # Slicing compressed Data
    c_set = file.get("subgroup/nested/compressed")
    slicec1 = c_set[0, 0, :]
    slicec2 = c_set[0, :, 0]
    slicec3 = c_set[:, 0, 0]
    slicec4 = c_set[:, 1:20, 1:20]
    slicec5 = c_set[1:20, 1:20, :]

    #Slicing chunked Data
    ch_set = file.get("subgroup/chunked")
    slicech1 = ch_set[0, 0, :]
    slicech2 = ch_set[0, :, 0]
    slicech3 = ch_set[:, 0, 0]
    slicech4 = ch_set[:, 1:20, 1:20]
    slicech5 = ch_set[1:20, 1:20, :]


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
    print(str(Timer(lambda: create_dataset("E:/asdsf.hdf", 100)).timeit(1)))
    # lp= LineProfiler()
    # lp_wrapper= lp(create_dataset)
    # lp.print_stats()