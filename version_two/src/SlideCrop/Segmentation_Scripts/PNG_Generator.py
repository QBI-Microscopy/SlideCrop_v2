from version_two.src.SlideCrop import ImarisImage as I
import numpy as np
import scipy.misc
DIRECTORY = "E:/testdata2"
import os
resolution = 4
directory = os.fsencode(DIRECTORY)
res_dir = "{}_resolution{}/".format(DIRECTORY, resolution)
if not os.path.exists(res_dir):
    os.makedirs(res_dir)

for filename in os.listdir(directory):
    file = filename.decode("utf-8")
    print(file)
    image = I.ImarisImage(DIRECTORY + "/" + file)
    image_array = image.get_two_dim_data(resolution)
    scipy.misc.imsave(res_dir + file[:-4] + ".jpg", image_array)
    del image
    del image_array