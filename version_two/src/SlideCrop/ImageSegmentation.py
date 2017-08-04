class ImageSegmentation(object):
    """
    Data Structure to hold box segments for images. Box segments are defined by two points: 
    upper-left & bottom-right.  
    """
    def __init__(self):
        pass

    def add_segmentation(self, x1, y1, x2, y2):
        """
        Adds a segmentation array to the ImageSegmentation object
        :param x1, y1: upper-left point of the segment box
        :param x2, y2: bottom-right point of the segment box
        :return: null
        """
        pass

    def get_scaled_segments(self, width, height):
        """
        :param width: pixel width of image to be scaled to.
        :param height: pixel height of image to be scaled to. 
        :return: An array of segment boxes scaled to the dimensions width x height
        """
        pass

    def get_relative_segments(self):
        """
        :return: An array of segment boxes without scaling.  0<= x, y <=1. 
        """
        pass

