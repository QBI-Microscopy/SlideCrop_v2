from .InputImage import InputImage
import numpy as np
import h5py
SEGMENTATION_DIMENSION_MAX = 20000000

class ImarisImage(InputImage):
    """
    Implementation of the InputImage interface for Imaris Bitplane files. 
    """
    def __init__(self, filename):
        """
        Constructor method
        :param filename: String path to the given image file. 
        """
        self.filename = filename
        self.file = h5py.File(self.filename, 'r')
        # will be defined as self.segmentation_resolution
        self._set_segmentation_res() # resolution level to be used for segmentation

    def get_two_dim_data(self, r, z=0, c=0, t=0, region=-1):
        """
        :param region: array of the form [x1, y1, x2, y2] for the 2D subregion desired. -1 implies the whole of 2D. 
        :return: ndarray of the given subset of the image as specified by the param. 
        """
        pass

    def get_euclidean_subset_in_resolution(self, r, c, x, y, z, t):
        """
        :param r: Resolution Level integer 
        :param c: [c1, c2] of channel range indexing. c2>=c1 
        :param x: [x1, x2] of x dimension indexing. x2>=x1
        :param y: [y1, y2] of y dimension indexing.  y2>=y1
        :param z: [z1, z2] of z dimension indexing. z2>=z1
        :param t: [t1, t2] of t dimension indexing. t2>=t1
        :return: ndarray of up to 5 dimensions for the image data of a given resolution in shape [c,x,y,z,t]
        """
        pass

    def get_low_res_image(self):
        """
        :return: A 2D image with the lowest resolutions at t=0, z=0, c=0
        """
        if (self.get_resolution_levels() != 0) && (self.get_channel_levels() != 0):
            return self.infile['/DataSet/ResolutionLevel {0}/TimePoint 0/Channel 0/Data'
                                .format(self.get_resolution_levels()-1)][0,:,:]
        # Else return empty Array of shape (0,0)
        return [[]];

    def get_segment_res_image(self):
        """
        The default segment resolution is the resolution level less than the default size,SEGMENTATION_DIMENSION_MAX. 
        :return: a 2D array of the image at the segmentation resolution. 
        """
        pass

    def get_resolution_levels(self):
        """
        :return: the number of resolution levels of the image 
        """
        return len(self.file['/DataSet'])

    def get_channel_levels(self):
        """
        :return: the number of channels the image has. 
        """
        channels = (self.infile['/DataSet/ResolutionLevel 0/TimePoint 0/'])
        return channels if channels != None else 0


    def change_segment_res(self, r):
        """
        Changes the resolution level used during segmentation. 
        :return: null
        """
        if (r>=0 && r<self.get_resolution_levels()):
            self.segment_resolution = r

    def _set_segmentation_res(self):
        image_dimensions = self.image_dimensions()
        resolution_level = 0
        while 1:
            shape = image_dimensions[resolution_level]
            return resolution_level if shape[0] * shape[1] <= SEGMENTATION_DIMENSION_MAX
            resolution_level+=1

    def resolution_dimensions(self, r):
        """
        Returns the size of each dimension for a given channel. Generally z,c,t will not change amongst resolutions. 
        :return: An array of the form [x, y, z, c, t]
        """
        base = "/DataSet/ResolutionLevel {0}/".format(r)

        t= len(self.file[base])
        c= len(self.file[base + "TimePoint 0/"])

        shape = self.file[base + "TimePoint 0/Channel 0/Data"].shape
        z= shape[0]
        y= shape[1]
        x = shape[2]
        return [x,y,z,c,t]


    def image_dimensions(self):
        """
        :return: a nested array of (x,y) sizes for all resolution levels by ascending resolution level number (0 first).
        """
        dimensionsStack = []
        i = self.get_resolution_levels() -1
        while i>=0:
            path = '/DataSet/ResolutionLevel {0}/TimePoint 0/Channel 0/Data'.format(i)
            y = self.file[path].shape[1]
            x = self.file[path].shape[2]
            dimensionsStack.append((y,x))
            i-=1
        return dimensionsStack

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
        Closes the associated file of the image. Good memory practice before removing this object or reference. 
        :return: null
        """
        self.file.close()