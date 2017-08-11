class ImageSegmentation(object):
    """
    Data Structure to hold box segments for images. Box segments are defined by two points: 
    upper-left & bottom-right.  
    """
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.segments = []

    def add_segmentation(self, x1, y1, x2, y2):
        """
        Adds a segmentation array to the ImageSegmentation object
        :param x1, y1: upper-left point of the segment box
        :param x2, y2: bottom-right point of the segment box
        :return: null
        """
        if (any(value < 0 for value in [x1, y1, x2, y2]) |
           any(x > self.width for x in [x1, x2])  |
           any(y > self.height for y in [y1, y2])):
           raise InvalidSegmentError
        else:
            self.segments.append([x1, y1, x2, y2])


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


class InvalidSegmentError(Exception):
    pass