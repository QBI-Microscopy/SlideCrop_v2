from InputImage import InputImage

class ImarisImage(InputImage):
    """
    Implementation of the InputImage interface for Imaris Bitplane files. 
    """
    def __init__(self, filename):
        """
        Constructor method
        :param filename: String path to the given image file. 
        """
        pass

    def get_two_dim_data(self, r, z=0, c=0, t=0, region=-1):
        """
        :param region: array of the form [x1, y1, x2, y2] for the 2D subregion desired. -1 implies the whole of 2D. 
        :return: ndarray of the given subset of the image as specified by the param. 
        """
        pass

    def get_euclidean_subset_in_resolution(self, r, c, x, y, z, t):
        """
        :param r: Resolution Level integer 
        :param c: [c1, c2] of channel ranges. c2>=c1 
        :param x: [x1, x2] of x dimension. x2>=x1
        :param y: [y1, y2] of y dimension. y2>=y1
        :param z: [z1, z2] of z dimension. z2>=z1
        :param t: [t1, t2] of t dimension. t2>=t1
        :return: ndarray of up to 5 dimensions for the image data of a given resolution
        """
        pass


    def get_low_res_image(self):
        """
        :return: A 2D image with the lowest resolutions at t=0, z=0, c=0
        """
        pass

    def get_segment_res_image(self):
        """
        The default segment resolution is the resolution level less than the default,SEGMENTATION_DIMENSION_MAX. 
        :return: a 2D array of the image at the segmentation resolution. 
        """
        pass

    def change_segment_res(self, r):
        """
        Changes the resolution level used during segmentation. 
        :return: null
        """
        pass

    def resolution_dimensions(self, r):
        """
        Returns the size of each dimension for a given channel. Generally z,c,t will not change amongst resolutions. 
        :return: An array of the form [x, y, z, c, t]
        """
        pass

    def image_dimensions(self):
        """
        :return: a nested array of (x,y) sizes for all resolution levels by ascending resolution level number (0 first).
        """
        pass

    def metadata_json(self):
        """
        :return: A JSON formatted structure of all the metadata for the image file. 
        """
        pass

    def metadata_from_path(self, path):
        """
        :param path: String representation of the nested path the the metadata. e.g. "metadata/timestamps/image_one" 
        :return: the value (singular or nested) from the metadata path specified. 
        """
        pass

    def close_file(self):
        """
        Closes the associated file of the image.
        :return: null
        """
        pass
