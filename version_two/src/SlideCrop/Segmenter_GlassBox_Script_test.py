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

def image_histogram_equalization(image, number_bins=256):
    # from http://www.janeriksolem.net/2009/06/histogram-equalization-with-python-and.html

    # get image histogram
    image_histogram, bins = np.histogram(image.flatten(), number_bins, normed=True)
    cdf = image_histogram.cumsum() # cumulative distribution function
    cdf = 255 * cdf / cdf[-1] # normalize

    # use linear interpolation of cdf to find new pixel values
    image_equalized = np.interp(image.flatten(), bins[:-1], cdf)

    return image_equalized.reshape(image.shape)


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
    structure = np.ones((20, 8))      # ((struct_size, struct_size))
    return  ndimage.binary_dilation(binary_image, structure=structure).astype(np.int)


WORK_DIR = "E:/"
im = io.imread(WORK_DIR + "testdata1_resolution4/AT8 wt2223m 11~B.jpg") #'trial.jpg') # "14864/1initial_photo.png") # "testdata1_resolution4/AT8 wt2223m 11~B.jpg") #'trial.jpg') # "_resolution4/170818_APP_1926_UII+O2_BF~B2combined.jpg") # 'trial.jpg') # "testdata1_resolution4/AT8 wt2223m 11~B.jpg")  # "14864/1initial_photo.png") # "testdata1_resolution4/AT8 wt2223m 11~B.jpg") # "14864/1initial_photo.png") # _resolution4/170818_APP_1926_UII+O2_BF~B2combined.jpg") # "testdata1_resolution4/AT8 wt2223m 11~B.jpg") # 'trial.jpg') # "testdata2_resolution3/170818_APP_1878 UII_BF~B.jpg") # "testdata3_resolution3/AVD M10 S21~B.jpg") # testdata1_resolution4/td1Image1.jpg") #   # "testdata1_resolution3/AT8 wt2223m 11~B.jpg") #"testdata2_resolution3/170818_APP_1878 UII_BF~B.jpg") #'testfile4.jpg') #"testdata1_resolution3/AT8 wt2223m 11~B.jpg") #  'testfile4.jpg') # "testdata2_resolution4/170818_APP_1878 UII_BF~B.jpg") # "'td11.png') # 'testfile4.jpg')
im = misc.imresize(im, size= (3000, 1200))
histogram = seg._image_histogram(im)
cluster = seg._k_means_iterate(histogram, 5)

print(cluster)

res_dir = "{}{}/".format(WORK_DIR, os.getpid())
if not os.path.exists(res_dir):
    os.makedirs(res_dir)

channel_im = seg._optimal_thresholding_channel_image(im)
misc.imsave("{}{}".format(res_dir, "1initial_photo.png"), channel_im)
print("Initial photo saved")

# channel_im = image_histogram_equalization(channel_im, 50)
misc.imsave("{}{}".format(res_dir, "1zinitial_photo.png"), channel_im)
print("Initial photo saved")


black_objects = seg._has_dark_objects(channel_im)
binary =  seg._apply_cluster_threshold(cluster, channel_im, seg._background_average_vector(channel_im)) # channel_im > 27

binary = binary.astype(int)
if black_objects:
    binary = 255 - binary
    black_objects = not black_objects

misc.imsave("{}{}".format(res_dir, "2thresholded_photo.png"), binary)
#del channel_im
print("thresholded image saved")

closed_image = _object_fill(binary)
misc.imsave("{}{}".format(res_dir, "3object_fill.png"), closed_image)
print("closed image saved")

opened_image = _noise_reduction(closed_image)
misc.imsave("{}{}".format(res_dir, "4noise_image.png"), opened_image)
print("opened image saved")

imlabeled, num_features = ndimage.measurements.label(opened_image, output=np.dtype("int")) #opened_image, output=np.dtype("int"))
sizes = ndimage.sum(opened_image, imlabeled, range(num_features + 1))
mask_size = sizes < 1000
misc.imsave("{}{}".format(res_dir, "5labels.png"), imlabeled)

# get non-object pixels and set to zero
remove_pixel = mask_size[imlabeled]
#imlabeled[remove_pixel] = 0
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


objs = ndimage.measurements.find_objects(imlabeled, max_label=len(labels))
# If any objects have been found, return
# return value will be array of tuple of 2 slice Objects
# [(slice(0, 2, None), slice(0, 3, None)), (slice(2, 5, None), slice(2, 5, None))]
# Analogous to label_clean[0:2, 0:3] for the first tuple
objs = filter(None, objs)
objs = sorted(objs)
print(len(objs))


def is_noise (s1):
    if (s1[0].stop - s1[0].start )*(s1[1].stop - s1[1].start )  < 1000:
        return True
    return False


def intersect (s1, s2):
    DELTAY = 50
    DELTAX = 20
    """
    :param s1, s2: 2D tuples of slice objects i.e. (Slice, Slice) for a region of an image. 
    :return: 1 if the intersection of the two regions is not empty (i.e. have common pixels)
    """
    if ( s1[0].stop + DELTAX < s2[0].start) | (s1[0].start > s2[0].stop + DELTAX):
        return False
    return not ( s1[1].stop + DELTAY < s2[1].start) | (s1[1].start > s2[1].stop + DELTAY)

def add(s1, s2):
    """
    :param s1, s2: 2D tuples of slice objects i.e. (Slice, Slice) for a region of an image. 
    :return: a 2D tuple of slice objects for a region of an image that contains both s1 and s2. 
    """
    x_values = [s1[0].start, s2[0].start, s1[0].stop, s2[0].stop]
    y_values = [s1[1].start, s2[1].start, s1[1].stop, s2[1].stop]
    x_slice = slice(min(x_values), max(x_values))
    y_slice = slice(min(y_values), max(y_values))
    return (x_slice, y_slice)


prev_len = len(objs)
curr_len = len(objs)
i = 0
flag = True


for i in range(10):
    for rect in objs:
        if is_noise(rect):

            objs.remove(rect)

for i in objs :
    print(i)

while flag | (prev_len != curr_len):
    print("objs left: {}".format(len(objs)))
    flag = False

    temp_list = []
    i = 0
    while i < (len(objs) -1 ):
        add_this_obj = 1

        j = i+1
        x1 = objs[i][0]
        x2  = objs[j][0]
        while (not ( x1.stop < x2.start) | (x1.start > x2.stop))  & (j < len(objs)):
            if intersect(objs[i], objs[j]):
                print("i {}, j {} ".format(objs[i], objs[j]))
                temp_list.append(add(objs.pop(j), objs.pop(i)))
                add_this_obj = 0
                j = len(objs) + 1
            else:
                j += 1
                if j < len(objs):
                    x2 = objs[j][0]
                else:
                    j = len(objs)

        if add_this_obj:
            print("adding i = {}, objs[i] = {}".format(i, objs[i]))
            temp_list.append(objs[i])
            i += 1

    print("objs left {}".format(objs))
    if len(objs) != 0:
        print("Zadding i = {}, objs[i] = {}".format(i, objs[-1]))
        # print("objs: {}".format(len(objs)))
        # print("i {} = {}".format(len(objs) -1, objs[-1]))
        temp_list.append(objs[-1])

    objs = sorted(temp_list.copy())
    del temp_list

    prev_len = curr_len
    curr_len = len(objs)
    i = 0
    print("END OF main while length of temp_list {0}\n\n".format(curr_len))

for i in objs :
    print(i)

for i in range(len(objs)):
    misc.imsave("{}8crop{}.png".format(res_dir, str(i)), channel_im[objs[i]]) # label_clean[objs[i]])
