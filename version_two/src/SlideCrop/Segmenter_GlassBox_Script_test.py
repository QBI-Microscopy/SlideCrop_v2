from version_two.src.SlideCrop.ImageSegmenter import ImageSegmenter as seg
from skimage import io
import scipy.misc as misc
import os
import numpy as np
import scipy.ndimage as ndimage


def _noise_reduction(binary_image):
    """
    Applies morphological opening to the binary_image to reduce noise. 
    :param binary_image: image to be opened.
    :return: A new binary image that has undergone opening. 
    """
    struct_size = 2 # max(round(binary_image.size / 8000000), 2)
    structure = np.ones((struct_size, struct_size))

    return ndimage.binary_erosion(binary_image, structure=structure, iterations=2).astype(np.int)


def _object_fill(binary_image):
    """
    Applies morphological closing to the binary_image to increase size of the foreground objects
    :param binary_image: image to be opened.
    :return: A new binary image that has undergone opening. 
    """
    struct_size = 5  # int(min(binary_image.shape) * 0.01)
    structure = np.ones((struct_size, struct_size))

    return ndimage.binary_dilation(binary_image, structure=structure, iterations=5).astype(np.int)


WORK_DIR = "E:/"
im = io.imread(WORK_DIR +   'td11.png') # 'testfile4.jpg')
histogram = seg._image_histogram(im)
cluster = seg._k_means_iterate(histogram, 6)

print(cluster)

res_dir = "{}{}/".format(WORK_DIR, os.getpid())
if not os.path.exists(res_dir):
    os.makedirs(res_dir)

channel_im = seg._optimal_thresholding_channel_image(im)
misc.imsave("{}{}".format(res_dir, "1initial_photo.png"), channel_im)
print("Initial photo saved")
black_objects = seg._has_dark_objects(channel_im)
print(black_objects)
binary = seg._apply_cluster_threshold(cluster, channel_im, seg._background_average_vector(channel_im))

binary = binary.astype(int)
if black_objects:
    binary = 255 - binary
    black_objects = not black_objects

misc.imsave("{}{}".format(res_dir, "2thresholded_photo.png"), binary)
del channel_im
print("thresholded image saved")

opened_image = _noise_reduction(binary)
misc.imsave("{}{}".format(res_dir, "3noise_image.png"), opened_image)
print("opened image saved")

closed_image = _object_fill(opened_image)
misc.imsave("{}{}".format(res_dir, "4object_fill.png"), closed_image)
print("closed image saved")

labelled_image, objects = ndimage.label(closed_image)
misc.imsave("{}{}".format(res_dir, "5labelled.png"), labelled_image)

segmentation = 25 * seg._apply_object_detection(binary)
print(segmentation.get_scaled_segments(closed_image.shape[0], closed_image.shape[1]))

"""
dark objects backgrounds must have 
"""
