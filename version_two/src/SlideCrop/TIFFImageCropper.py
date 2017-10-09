import os
from version_two.src.SlideCrop.ImageSegmentation import ImageSegmentation as ImageSegmentation
import numpy as np
import scipy.ndimage as ndimage
import scipy.misc as misc
import tifffile

class TIFFImageCropper(object):
    """
    Implementation of the ImageCropper interface for the cropping of an inputted image over all dimensions such that the
    ImageSegmentation object applies to each x-y plane and the output is in TIFF format. 
    """
    @staticmethod
    def crop_input_images(input_image, image_segmentation, output_path):
        """
        Crops the inputted image against the given segmentation. All output files will be saved to the OutputPath
        :param input_image: An InputImage object. 
        :param image_segmentation: ImageSegmentation object with already added segments
        :param output_path: String output path must be a directory
        :return: 
        """
        if not os.path.isdir(output_path):
            return None

        ## Iterate through each bounding box
        for box_index in range(len(image_segmentation.segments)):
            TIFFImageCropper.crop_single_image(input_image, image_segmentation, output_path, box_index)


    @staticmethod
    def crop_single_image(input_image, image_segmentation, output_path, box_index):
        ## Create New, empty Tiff file.
        output_filename  = "{}/{}_{}.tif".format(output_path, input_image.get_filename(), box_index)

        for r_lev in range(input_image.get_resolution_levels()):
            ## Create a 3dim image to include all the channels (do we want times as fourth dimension)
            resolution_dimensions = input_image.image_dimensions()[r_lev]
            segment = image_segmentation.get_scaled_segments(resolution_dimensions[0], resolution_dimensions[1])[box_index]

            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)

            # image data with dimensions [c,x,y,z,t]
            image_data = input_image.get_euclidean_subset_in_resolution(r = r_lev,
                                                                        t = [0, t],
                                                                        c= [0, c],
                                                                        z =[0, z],
                                                                        y = [segment[1], segment[3]],
                                                                        x = [segment[0], segment[2]])

            ## Append to existing file on all resolutions except resolution = 0
            to_append = r_lev != 0
            tifffile.imsave(output_path, data=image_data, append=to_append, software="SlideCrop 2")

            ## clear memory by removing as many variables as possible
            del image_data
