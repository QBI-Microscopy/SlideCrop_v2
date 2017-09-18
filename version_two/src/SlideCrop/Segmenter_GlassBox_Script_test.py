from version_two.src.SlideCrop.ImageSegmenter import ImageSegmenter as seg
from skimage import io
import scipy.misc as misc
import os
import numpy as np
import scipy.ndimage as ndimage

## NOTES
"""
image size around 1000/1500 * 3000/3600
"""

def _noise_reduction(binary_image):
    """
    Applies morphological opening to the binary_image to reduce noise. 
    :param binary_image: image to be opened.
    :return: A new binary image that has undergone opening. 
    """
    struct_size = 3 # max(round(binary_image.size / 8000000), 2)
    structure = np.ones((struct_size, struct_size))
    return ndimage.binary_erosion(binary_image, structure=structure, iterations=2).astype(np.int)


def _object_fill(binary_image):
    """
    Applies morphological closing to the binary_image to increase size of the foreground objects
    :param binary_image: image to be opened.
    :return: A new binary image that has undergone opening. 
    """
    struct_size = 20  # int(min(binary_image.shape) * 0.01)
    structure = np.ones((struct_size, struct_size))
    return  ndimage.binary_fill_holes(binary_image, structure=structure).astype(np.int)
    #return ndimage.binary_dilation(binary_image, structure=structure, iterations= 2).astype(np.int)

WORK_DIR = "E:/"
im = io.imread(WORK_DIR + "testdata2_resolution3/170818_APP_1878 UII_BF~B.jpg") # "testdata1_resolution3/AT8 wt2223m 11~B.jpg") #"testdata2_resolution3/170818_APP_1878 UII_BF~B.jpg") # "testdata1_resolution3/AT8 wt2223m 11~B.jpg") #'testfile4.jpg') #"testdata1_resolution3/AT8 wt2223m 11~B.jpg") #  'testfile4.jpg') # "testdata2_resolution4/170818_APP_1878 UII_BF~B.jpg") # "'td11.png') # 'testfile4.jpg')
im = misc.imresize(im, size= (3000, 1200))
print(im.shape)
histogram = seg._image_histogram(im)
cluster = seg._k_means_iterate(histogram, 5)

print(cluster)

res_dir = "{}{}/".format(WORK_DIR, os.getpid())
if not os.path.exists(res_dir):
    os.makedirs(res_dir)

channel_im = seg._optimal_thresholding_channel_image(im)
misc.imsave("{}{}".format(res_dir, "1initial_photo.png"), channel_im)
print("Initial photo saved")
black_objects = seg._has_dark_objects(channel_im)
binary = seg._apply_cluster_threshold(cluster, channel_im, seg._background_average_vector(channel_im))

binary = binary.astype(int)
if black_objects:
    binary = 255 - binary
    black_objects = not black_objects

misc.imsave("{}{}".format(res_dir, "2thresholded_photo.png"), binary)
del channel_im
print("thresholded image saved")

closed_image = _object_fill(binary)
misc.imsave("{}{}".format(res_dir, "3object_fill.png"), closed_image)
print("closed image saved")

opened_image = _noise_reduction(closed_image)
misc.imsave("{}{}".format(res_dir, "4noise_image.png"), opened_image)
print("opened image saved")

imlabeled, num_features = ndimage.measurements.label(opened_image, output=np.dtype("int"))
sizes = ndimage.sum(opened_image, imlabeled, range(num_features + 1))
mask_size = sizes < 1000
misc.imsave("{}{}".format(res_dir, "5labels.png"), imlabeled)

# get non-object pixels and set to zero
remove_pixel = mask_size[imlabeled]
imlabeled[remove_pixel] = 0
labels = np.unique(imlabeled)
misc.imsave("{}{}".format(res_dir, "6removepixel.png"), imlabeled)

labelled_image, objects = ndimage.label(imlabeled)
print("number {}, {}".format(np.max(labelled_image), objects))
misc.imsave("{}{}".format(res_dir, "7labelled.png"), labelled_image + 1)

# ndimage
label_clean = np.searchsorted(labels, imlabeled)

# Iterate through range and make array of 0, 1, ..., len(labels)
lab = []
for i in range(len(labels) - 1):
    lab.append(i + 1)


objs = ndimage.measurements.find_objects(label_clean, max_label=len(labels))
# If any objects have been found, return
# return value will be array of tuple of 2 slice Objects
# [(slice(0, 2, None), slice(0, 3, None)), (slice(2, 5, None), slice(2, 5, None))]
# Analogous to label_clean[0:2, 0:3] for the first tuple
objs = filter(None, objs)
objs = sorted(objs)
print(len(objs))

def intersect (s1, s2):
    if ( s1[0].stop < s2[0].start) | (s1[0].start > s2[0].stop):
        return False
    return not ( s1[1].stop < s2[1].start) | (s1[1].start > s2[1].stop)

def add(s1, s2):
    x_values = [s1[0].start, s2[0].start, s1[0].stop, s2[0].stop]
    y_values = [s1[1].start, s2[1].start, s1[1].stop, s2[1].stop]
    x_slice = slice(min(x_values), max(x_values))
    y_slice = slice(min(y_values), max(y_values))
    return (x_slice, y_slice)

prev_len = len(objs)
curr_len = len(objs)
i = 0
flag = True
print((prev_len, curr_len))
print((prev_len != curr_len) | flag)
print(objs)
while flag | (prev_len != curr_len):
    flag = False
    while i < (len(objs) -1):
        if(intersect(objs[i], objs[i+1])):
            objs.append(add(objs.pop(i+1), objs.pop(i)))
            print("true")
        i+=1

    objs = sorted(objs)
    print(len(objs))
    prev_len = curr_len
    curr_len = len(objs)
    i = 0

print(objs)

for i in range(len(objs)):
    misc.imsave("{}8crop{}.png".format(res_dir, str(i)), label_clean[objs[i]])
