from .ImageSegmentation import ImageSegmentation
import numpy as np
import scipy.ndimage as ndimage
import scipy.misc as misc

K_Clusters = 10
BGPCOUNT = 80  # Background Pixel Count: Pixel length of the squares to be used in the image corners.
SENSITIVITY_THRESHOLD = .05
ITERATIONS = 2


class ImageSegmenter(object):
    """
    Static Methods to segment an 2D image with multiple channels. 
    Primary method segment_image() uses the following implementation: 
        1. Thresholding the image to find a binary image through a k means clustering on the histogram. 
        2. Morpological opening(erosion then dilation) for noise reduction
         and detail blurring. 
        3. 
    """

    @staticmethod
    def segment_image(image_array):
        """
        Segments the image by means of mathematical morphology.
        :param image_array: a 2D image array to be cropped with an optional channel dimension Shape in form (c,y,x)
         where c >=1
        :return: an ImageSegmentation object 
        """
        binary_image = ImageSegmenter._threshold_image(misc.imresize(image_array, size=(3000, 1200)), K_Clusters)
        opened_image = ImageSegmenter._image_dilation(binary_image)
        closed_image = ImageSegmenter._noise_reduction(opened_image)
        return ImageSegmenter._apply_object_detection(closed_image)

    @staticmethod
    def _threshold_image(image_array, k):
        """
        Handler to properly threshold the image_array to a binary image of
        foreground and background. Algorithm used is a k-means clustering. 
        :param image_array: 
        :return: a 2D binary image
        """
        channel_image = ImageSegmenter._construct_mean_channelled_image(image_array)
        histogram = ImageSegmenter._image_histogram(channel_image)
        cluster_vector = ImageSegmenter._k_means_iterate(histogram, k)
        return ImageSegmenter._apply_cluster_threshold(cluster_vector, channel_image,
                                                       ImageSegmenter._has_dark_objects(channel_image))

    @staticmethod
    def _has_dark_objects(image):
        """
        :return: True if the image parameter has black foreground images on a light background, false otherwise. 
        """
        mean_background_vector = ImageSegmenter._background_average_vector(image)
        return (mean_background_vector > 127)

    @staticmethod
    def _background_average_vector(image):
        """
        :return: the average background pixel intensity for the four corners of the image in each channel. 
        """
        x_dim = image.shape[0]
        y_dim = image.shape[1]

        background_index_x_list = []
        background_index_y_list = []

        # Add indices for each corner of the image
        for i in range(BGPCOUNT):
            background_index_x_list.append(i);
            background_index_y_list.append(i);
            background_index_x_list.append(x_dim - (i + 1));
            background_index_y_list.append(y_dim - (i + 1));

        if image.ndim == 3:
            # Create a image vector with pixel values from the 2D corners of all channels. Used as a background intensity mean.
            background_vector = image[background_index_x_list, background_index_y_list, :]
            return np.mean(np.mean(background_vector, axis=1), axis=0)
        else:
            background_vector = image[background_index_x_list, background_index_y_list]
            return np.mean(background_vector)

    @staticmethod
    def _construct_mean_channelled_image(image):
        """
        :param image: a 2D image array to be cropped with an optional channel dimension Shape in form (c,y,x)
         where c >=1
        :return: a purely 2D image by averaging the pixel intensities across the channels. 
        """
        if image.ndim == 3:
            return np.mean(image, axis=0)
        return image

    @staticmethod
    def _optimal_thresholding_channel_image(image):
        """
        Handles a 2Darray of multiple channels and determines the best channel to apply thresholding to. 
        :param image: 3Darray image of a 2D image with multiple channels
        :return: a 2Darray of the image from the best channel
        """
        x_dim = image.shape[0]
        y_dim = image.shape[1]

        if image.ndim == 3:
            # Find mean intensity for each channel
            # Averaged across axis separately. Shape = (x,y,3) -> (x -> 3) -> (1,3)
            channel_mean_vector = np.mean(np.mean(image, axis=1), axis=0)

            background_channel_mean_vector = ImageSegmenter._background_average_vector(image)

            # Choose channel for clustering based on maximum difference in background and average intensity
            max_difference_channel = np.abs(background_channel_mean_vector - channel_mean_vector)
            clustering_channel = np.argmax(max_difference_channel)
            return image[:, :, clustering_channel]
        return image.copy()

    @staticmethod
    def _image_histogram(channel_image):
        """
        Creates a histogram from a 2D channel image/ 
        :param channel_image: 2D array
        :return: a 1D array of length 256 where the index represents the pixel intensity [0,255] and the value in each
        cell is the number of pixels of that intensity from the channel_image
        """
        histogram = np.zeros((256))
        for pixel in channel_image:
            histogram[pixel] += 1
        return histogram

    @staticmethod
    def _k_means_iterate(histogram, k):
        """
        K-means algorithm from a histogram based implementation. 
        :param k: number of clusters for the algorithm
        :return: a vector of size k of the clusters' pixel intensities
        """

        def closest_index(ndarray, value):
            """
            Helper Method: returns the index in ndarray of the number which is closest to value. 
            """
            return np.argmin(np.abs(ndarray - value))

        # Initiate k clusters equidistant on the domain of the channel intensity
        cluster_vector = np.linspace(0, 255, num=k)
        cluster_temp_vector = cluster_vector.copy()

        while (1):

            # Find closest cluster for each pixel intensity in histogram
            index_histogram = [closest_index(cluster_vector, i) for i in range(256)]

            # for each cluster, find mean of clustered pixel intensities
            # histogram[i] is number of pixels at intensity i
            for k in range(k):
                weighted_mean_sum = sum(ind * histogram[ind] for ind in range(256) if index_histogram[ind] == k)
                pixel_count = sum(histogram[ind] for ind in range(256) if index_histogram[ind] == k)
                cluster_temp_vector[k] = weighted_mean_sum / (pixel_count + 1)

            # If all clusters change less than the threshold -> finish iteration
            if (np.abs((cluster_vector - cluster_temp_vector)) <= SENSITIVITY_THRESHOLD).all():
                return cluster_temp_vector
            cluster_vector = cluster_temp_vector.copy()

    @staticmethod
    def _apply_cluster_threshold(cluster_vector, channel_image, darkObjects):
        """
        Applies the cluster_vector thresholds to the channel_image to create a binary image. 
        :param cluster_vector: 1D array of cluster pixel intensities
        :param channel_image: 2D image array
        :return: a binary image of the median threshold from cluster_vector
        """
        if (darkObjects):
            binary_threshold = cluster_vector[-2]
            return 255 - (255 * (channel_image > binary_threshold).round())

        else:
            binary_threshold = cluster_vector[1]
            return 255 * (channel_image > binary_threshold).round()

    @staticmethod
    def _apply_morphological_opening(binary_image):
        """
        Applies morphological opening to the binary_image to reduce noise. 
        :param binary_image: image to be opened.
        :return: A new binary image that has undergone opening. 
        """
        struct_size = int(min(binary_image.shape) * 0.005)
        structure = np.ones((struct_size, struct_size))
        return ndimage.binary_opening(binary_image, structure=structure, iterations=ITERATIONS).astype(np.int)

    @staticmethod
    def _apply_morphological_closing(binary_image):
        """
        Applies morphological closing to the binary_image to increase size of the foreground objects
        :param binary_image: image to be opened.
        :return: A new binary image that has undergone opening. 
        """
        struct_size = int(min(binary_image.shape) * 0.005)
        structure = np.ones((struct_size, struct_size))
        return ndimage.binary_closing(binary_image, structure=structure, iterations=ITERATIONS).astype(np.int)

    def _noise_reduction(binary_image):
        """
        Applies morphological erosion to the binary_image to reduce noise. 
        :param binary_image: image to be opened.
        :return: A new binary image that has undergone opening. 
        """
        struct_size = 3  # max(round(binary_image.size / 8000000), 2)
        structure = np.ones((struct_size, struct_size))
        return ndimage.binary_erosion(binary_image, structure=structure, iterations=2).astype(np.int)

    def _image_dilation(binary_image):
        """
        Applies morphological dilation to the binary_image to increase size of the foreground objects
        :param binary_image: image to be opened.
        :return: A new binary image that has undergone opening. 
        """
        struct_size = 20  # int(min(binary_image.shape) * 0.01)
        structure = np.ones((20, 8))  # ((struct_size, struct_size))
        return ndimage.binary_dilation(binary_image.astype(np.int), structure=structure)

    @staticmethod
    def _apply_object_detection(morphological_image):
        """
        Detects foreground objects from a binary, opened image. 
        :param morphological_image: Binary image
        :return: A ImageSegmentation object
        """
        segmentations = ImageSegmentation(morphological_image.shape[0], morphological_image.shape[1])

        imlabeled, num_features = ndimage.measurements.label(morphological_image, output=np.dtype("int"))
        # sizes = ndimage.sum(morphological_image, imlabeled, range(num_features + 1))
        # mask_size = sizes < 1000
        #
        # # get non-object pixels and set to zero
        # remove_pixel = mask_size[imlabeled]
        labels = np.unique(imlabeled)
        # labelled_image, objects = ndimage.label(imlabeled)
        # label_clean = np.searchsorted(labels, imlabeled)

        # Iterate through range and make array of 0, 1, ..., len(labels)
        lab = []
        for i in range(len(labels) - 1):
            lab.append(i + 1)

        objs = ndimage.measurements.find_objects(imlabeled, max_label=len(labels))

        # filter out None values and sort the objs
        objs = filter(None, objs)
        objs = sorted(objs)

        #  apply construction of subslices to form larger sized images
        objs = ImageSegmenter._reconstruct_images_from_slices(objs)

        # add to ImageSegmenter data structure
        for box in objs:
            ImageSegmenter._add_box_from_slice(box, segmentations)

        ######################### Used for testing purposes only to check segments are correct ########################
        #
        # for i in range(len(objs)):
        #     misc.imsave("E:/8crop{}.png".format(str(i)), imlabeled[objs[i]])
        #

        return segmentations

    @staticmethod
    def _add_box_from_slice(box, segmentation_object):
        """
        returns an array of two points [x1, y1, x2, y2] where point 1 is the left top corner and point 2 the right
         bottom corner of a box surrounding an object. 
        :param box: a 2 value tuple of slice objects
        """

        y_slice = box[1]
        x_slice = box[0]
        segmentation_object.add_segmentation(x_slice.start, y_slice.start, x_slice.stop, y_slice.stop)

    @staticmethod
    def is_noise(s1):
        """
        Checks if the slice object should be considered as noise pixels and not constructive of a larger image. 
        :param s1: slice object tuple
        :return:  True if the area of the bounding box is less than 1000 pixels
        """
        if (s1[0].stop - s1[0].start) * (s1[1].stop - s1[1].start) < 1000:
            return True
        return False

    @staticmethod
    def intersect(s1, s2):
        """
        :param s1, s2: 2D tuples of slice objects i.e. (Slice, Slice) for a region of an image. 
        :return: 1 if the intersection of the two regions is not empty (i.e. have common pixels) for a given buffer 
            DELTAX or DELTAX
        """
        DELTAY = 50
        DELTAX = 20

        if (s1[0].stop + DELTAX < s2[0].start) | (s1[0].start > s2[0].stop + DELTAX):
            return False
        return not (s1[1].stop + DELTAY < s2[1].start) | (s1[1].start > s2[1].stop + DELTAY)

    @staticmethod
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

    @staticmethod
    def _reconstruct_images_from_slices(box_slices):
        """
        Iterative process to continuously add intersecting  
        :param box_slices: List of slice tuples considered as bounding boxes for an image. 
        :return: a new list of bounding boxes that are the reconstructed bounding boxes for the images in the photo. 
        """
        prev_len = len(box_slices)
        curr_len = len(box_slices)
        flag = True

        for i in range(10):
            for rect in box_slices:
                if ImageSegmenter.is_noise(rect):
                    box_slices.remove(rect)

        while flag | (prev_len != curr_len):
            flag = False

            temp_list = []
            i = 0
            while i < (len(box_slices) - 1):
                add_this_obj = 1

                j = i + 1
                x1 = box_slices[i][0]
                x2 = box_slices[j][0]
                while (not (x1.stop < x2.start) | (x1.start > x2.stop)) & (j < len(box_slices)):
                    if ImageSegmenter.intersect(box_slices[i], box_slices[j]):
                        temp_list.append(ImageSegmenter.add(box_slices.pop(j), box_slices.pop(i)))
                        add_this_obj = 0
                        j = len(box_slices) + 1
                    else:
                        j += 1
                        if j < len(box_slices):
                            x2 = box_slices[j][0]
                        else:
                            j = len(box_slices)

                if add_this_obj:
                    temp_list.append(box_slices[i])
                    i += 1

            if len(box_slices) != 0:
                temp_list.append(box_slices[-1])

            box_slices = sorted(temp_list.copy())
            del temp_list

            prev_len = curr_len
            curr_len = len(box_slices)
            i = 0

        # TODO: remove more objects that aren't big enough to be considered full images.
        return box_slices
