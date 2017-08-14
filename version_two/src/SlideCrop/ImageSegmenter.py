from .ImageSegmentation import ImageSegmentation
import numpy as np
import scipy.ndimage as ndimage
class ImageSegmenter(object):
    """
    Static Methods to segment an 2D image 
    """
    @staticmethod
    def segment_image(image_array):
        """
        Segments the image by means of mathematical morphology.
        :param image_array: a 2D image array to be cropped 
        :return: an ImageSegmentation object 
        """

        # Find appropriate size of erosion structure\ Default just 5x5 +
        structure = np.zeros((5,5))
        structure[2,:] = 1
        structure[:,2] = 1
        ndimage.binary_erosion(image_array, structure= structure,
                                output=image_array, )