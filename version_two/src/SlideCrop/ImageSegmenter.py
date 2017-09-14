from .ImageSegmentation import ImageSegmentation
import numpy as np
import scipy.ndimage as ndimage

K_Clusters = 10
BGPCOUNT = 80  # Background Pixel Count: Pixel length of the squares to be used in the image corners.
SENSITIVITY_THRESHOLD = 0.01
ITERATIONS = 2

class ImageSegmenter(object):

    """
    Static Methods to segment an 2D image. 
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
        :param image_array: a 2D image array to be cropped 
        :return: an ImageSegmentation object 
        """
        binary_image = ImageSegmenter._threshold_image(image_array, K_Clusters)
        opened_image = ImageSegmenter._apply_morphological_opening(binary_image)
        closed_image = ImageSegmenter._apply_morphological_closing(opened_image)
        return ImageSegmenter._apply_object_detection(closed_image)



    @staticmethod
    def _threshold_image(image_array, k):
        """
        Handler to properly threshold the image_array to a binary image of
        foreground and background. Algorithm used is a k-means clustering. 
        :param image_array: 
        :return: a 2D binary image
        """
        channel_image = ImageSegmenter._optimal_thresholding_channel_image(image_array)
        histogram = ImageSegmenter._image_histogram(channel_image)
        cluster_vector = ImageSegmenter._k_means_iterate(histogram, k)
        return ImageSegmenter._apply_cluster_threshold(cluster_vector, channel_image)

    @staticmethod
    def _has_dark_objects(image):
        mean_background_vector = ImageSegmenter._background_average_vector(image)
        print(mean_background_vector)
        return (mean_background_vector > 127)


    @staticmethod
    def _background_average_vector(image):
        x_dim = image.shape[0]
        y_dim = image.shape[1]

        background_index_x_list = []
        background_index_y_list = []
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

            background_channel_mean_vector = ImageSegmenter._optimal_thresholding_channel_image(image)

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
        cluster_vector = np.linspace(0, 255, num = k)
        cluster_temp_vector = cluster_vector.copy()

        while (1):

            # Find closest cluster for each pixel intensity in histogram
            index_histogram = [closest_index(cluster_vector, i) for i in range(256)]

            # for each cluster, find mean of clustered pixel intensities
            # histogram[i] is number of pixels at intensity i
            for k in range(k):
                weighted_mean_sum = sum(ind * histogram[ind] for ind in range(256) if index_histogram[ind] == k)
                pixel_count = sum(histogram[ind] for ind in range(256) if index_histogram[ind] == k)
                cluster_temp_vector[k] = weighted_mean_sum / (pixel_count  +1)

            # If all clusters change less than the threshold -> finish iteration
            if (np.abs(cluster_vector / cluster_temp_vector - 1) < SENSITIVITY_THRESHOLD).all():
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
        if(darkObjects):
            binary_threshold = cluster_vector[-2]
            return 255 * (channel_image > binary_threshold).round()
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
        return ndimage.binary_opening(binary_image, structure= structure, iterations= ITERATIONS).astype(np.int)

    @staticmethod
    def _apply_morphological_closing(binary_image):
        """
        Applies morphological closing to the binary_image to increase size of the foreground objects
        :param binary_image: image to be opened.
        :return: A new binary image that has undergone opening. 
        """
        struct_size = int(min(binary_image.shape) * 0.005)
        structure = np.ones((struct_size, struct_size))
        return ndimage.binary_closing(binary_image, structure=structure, iterations= ITERATIONS).astype(np.int)

    @staticmethod
    def _apply_object_detection(morphological_image):
        """
        Detects foreground objects from a binary, opened image. 
        :param morphological_image: Binary image
        :return: A ImageSegmentation object
        """
        segmentations = ImageSegmentation(morphological_image.shape[0], morphological_image.shape[1])
        if not ImageSegmenter._has_dark_objects(morphological_image):
            morphological_image = 255- morphological_image
        labelled_image, objects = ndimage.label(morphological_image)
        object_list = ndimage.find_objects(labelled_image, objects)
        print("objects")
        print(object_list)
        for box in object_list:
            box_dim = ImageSegmenter._get_box_from_slice(box)
            #segmentations.add_segmentation(box_dim[0], box_dim[1], box_dim[2], box_dim[3])
        return segmentations

    @staticmethod
    def _get_box_from_slice(box):
        """
        returns an array of two points [x1, y1, x2, y2] where point 1 is the left top corner and point 2 the right
         bottom corner of a box surrounding an object. 
        :param box: a 2 value tuple of slice objects
        :return: an array of form [x1, y1, x2, y2] 
        """
        # y_slice = box[1]
        # x_slice = box[0]
        # return [x_slice.start, y_slice.start, x_slice.stop, y_slice.stop]
        #

