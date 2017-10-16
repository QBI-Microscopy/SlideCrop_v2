import os
from version_two.src.SlideCrop.ImageSegmentation import ImageSegmentation as ImageSegmentation
import numpy as np
import scipy.ndimage as ndimage
import scipy.misc as misc
import tifffile

#  TODO: need to encode bigtiff requirement
#  TODO: repackage tiff resolutions into single image with ability to retrieve them
#  TODO: need to reallign dimension ordering to be more compatible with ImageJ
#  TODO: look into time bottlenecks.
#  TODO: consider compression



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
    #  TODO: check with Liz the format wanted...
    def crop_single_image(input_image, image_segmentation, output_path, box_index):
        ## Create New, empty Tiff file.
        # output_filename  = "{}/{}_{}.tif".format(output_path, input_image.get_name(), box_index)

        for r_lev in range(input_image.get_resolution_levels()):
            output_filename = "{}/{}_{}.tif".format(output_path, input_image.get_name(), box_index)

            ## Create a 3dim image to include all the channels (do we want times as fourth dimension)
            resolution_dimensions = input_image.image_dimensions()[r_lev]
            image_segmentation1 = image_segmentation # image_segmentation.handle_shift_factor(resolution_dimensions[1], resolution_dimensions[0])
            segment = image_segmentation1.get_scaled_segments(resolution_dimensions[1], resolution_dimensions[0])[box_index]

            # print("new segment box scaled", r_lev)
            # print(segment)


            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)

            # image data with dimensions [c,x,y,z,t]
            image_data = input_image.get_euclidean_subset_in_resolution(r = r_lev,
                                                                        t = [0, t],
                                                                        c= [0, c],
                                                                        z =[0, z],
                                                                        y = [segment[1], segment[3]],
                                                                        x = [segment[0], segment[2]])

            print("r = {}, index = {}".format(r_lev, box_index))
            print("resolution  {} area {}".format(resolution_dimensions, segment))
            print("for found boxes at 3000x1200 and box {}".format(image_segmentation1.segments[box_index]))
            print(image_data.shape, image_data.dtype.itemsize)
            ## Append to existing file on all resolutions except resolution = 0
            to_append = r_lev != 0
            BIG_TIFF = 2**32-2**25
            is_big_tiff = (image_data.size * image_data.dtype.itemsize) > BIG_TIFF
            if(is_big_tiff):
                print("PRINTING A VERY BIG TIFF")
            tifffile.imsave(output_filename, data=image_data, append=to_append, bigtiff = is_big_tiff, software="SlideCrop 2")

            ## clear memory by removing as many variables as possible
            del image_data
            print("Dome")
            print("")

