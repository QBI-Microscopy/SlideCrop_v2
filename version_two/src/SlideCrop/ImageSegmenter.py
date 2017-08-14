from .ImageSegmentation import ImageSegmentation

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
        pass