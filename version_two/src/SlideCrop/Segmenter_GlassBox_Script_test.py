from version_two.src.SlideCrop.ImageSegmenter import ImageSegmenter as seg
from skimage import io
import scipy.misc as misc
import os
import numpy as np
import scipy.ndimage as ndimage


def _apply_morphological_opening(binary_image):
    """
    Applies morphological opening to the binary_image to reduce noise. 
    :param binary_image: image to be opened.
    :return: A new binary image that has undergone opening. 
    """
    struct_size = 2 #int(min(binary_image.shape) * 0.01)
    structure = np.ones((struct_size, struct_size))
    return ndimage.binary_opening(binary_image, structure=structure, iterations=1).astype(np.int)

def _apply_morphological_closing(binary_image):
    """
    Applies morphological closing to the binary_image to increase size of the foreground objects
    :param binary_image: image to be opened.
    :return: A new binary image that has undergone opening. 
    """
    struct_size = 20 #int(min(binary_image.shape) * 0.01)
    structure = np.ones((struct_size, struct_size))
    return ndimage.binary_closing(binary_image, structure=structure, iterations=2).astype(np.int)


WORK_DIR  = "E:/"
im = io.imread(WORK_DIR + 'biggerTest.png') # 'td11.png') # "testfile4.jpg") #
histogram = seg._image_histogram(im)
cluster = seg._k_means_iterate(histogram, 6)

print(cluster)

res_dir = "{}{}/".format(WORK_DIR, os.getpid())
if not os.path.exists(res_dir ):
    os.makedirs(res_dir)

channel_im = seg._optimal_thresholding_channel_image(im)
misc.imsave("{}{}".format(res_dir, "1initial_photo.png"), channel_im)
print("Initial photo saved")

binary  = seg._apply_cluster_threshold(cluster, channel_im, seg._background_average_vector(channel_im))
#binary = (1- binary).astype(int)
binary = binary.astype(int)

misc.imsave("{}{}".format(res_dir, "2thresholded_photo.png"), binary)
del channel_im
print("thresholded image saved")

opened_image = _apply_morphological_opening(binary)
misc.imsave("{}{}".format(res_dir, "3opened_photo.png"), opened_image)
print("opened image saved")

closed_image = _apply_morphological_closing(opened_image)
misc.imsave("{}{}".format(res_dir, "4closed_image.png"), closed_image)
print("closed image saved")

segmentation = seg._apply_object_detection(binary)
print(segmentation.get_scaled_segments(closed_image.shape[0], closed_image.shape[1]))

"""
dark objects backgrounds must have 
"""