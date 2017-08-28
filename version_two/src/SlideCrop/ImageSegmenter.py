from .ImageSegmentation import ImageSegmentation
import numpy as np
import scipy.ndimage as ndimage
class ImageSegmenter(object):
    """
    Static Methods to segment an 2D image. 
    Primary method segment_image() uses the following implementation: 
        1. Thresholding the image to find a binary image through a k means clustering. 
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

        # TODO: Find appropriate size of erosion structure
        # Default just 5x5 pixel in a '+' pattern
        structure = np.zeros((5,5))
        structure[2,:] = 1
        structure[:,2] = 1
        ndimage.binary_erosion(image_array, structure= structure,
                                output=image_array, )

    @staticmethod
    def _threshold_image(image_array):
        """
        Handler to properly threshold the image_array to a binary image of
        foreground and background. Algorithm used is a k-means clustering. 
        :param image_array: 
        :return: 
        """

