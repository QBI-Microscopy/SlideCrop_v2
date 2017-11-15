import os
from version_two.src.SlideCrop.ImageSegmentation import ImageSegmentation as ImageSegmentation
import numpy as np
import scipy.ndimage as ndimage
import scipy.misc as misc
import tifffile
from  skimage.io import MultiImage
import PIL.Image as Image
from PIL.TiffImagePlugin import AppendingTiffWriter as TIFF
import PIL.TiffImagePlugin as TIFFPlugin
import logging

from multiprocessing import Process
import version_two.src.SlideCrop.ImarisImage as I


#  TODO: Enable time and z dimension images
#  TODO: Fix "OverflowError: size does not fit in an int" from PIL dimensions sizes
#  TODO: Fix missing dimensions for ImageJ. Currently T and Z have been removed, but this makes ImageJ interprete
#  each resolution as a time dimension, which than tries to allocate res_levels * max dimensions of memory.
#   TODO: Channels > 3



class TIFFImageCropper(object):
    """
    Implementation of the ImageCropper interface for the cropping of an inputted image over all dimensions such that the
    ImageSegmentation object applies to each x-y plane and the output is in TIFF format. 
    """

    @staticmethod
    def crop_input_images(input_path, image_segmentation, output_path):
        """
        Crops the inputted image against the given segmentation. All output files will be saved to the OutputPath
        :param input_image: An InputImage object. 
        :param image_segmentation: ImageSegmentation object with already added segments
        :param output_path: String output path must be a directory
        :return: 
        """
        if not os.path.isdir(output_path):
            return None
        else:
            new_folder = (input_path.split("/")[-1]).split(".")[0]
            image_folder = "{}/{}".format(output_path, new_folder)
            if not os.path.isdir(image_folder):
                os.makedirs(image_folder)

        pid_list = []

        ## Iterate through each bounding box
        for box_index in range(len(image_segmentation.segments)):
            crop_process = Process(target=TIFFImageCropper.crop_single_image,
                                   args=(input_path, image_segmentation, image_folder, box_index))
            pid_list.append(crop_process)
            crop_process.start()
            # proc.join()  # Uncomment these two lines to allow single processing of ROIs. When commented
        # return           # the program will give individual processes a ROI each: multiprocessing to use more CPU.
        for proc in pid_list:
            proc.join()

    @staticmethod
    def crop_single_image(input_path, image_segmentation, output_path, box_index):
        input_image = I.ImarisImage(input_path)

        output_folder = "{}/ind{}".format(output_path, box_index)  # come up with better format
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)

        single_resolution_image_paths = []

        for r_lev in range(input_image.get_resolution_levels()):
            resolution_output_filename = "{}/{}_{}.tiff".format(output_folder, input_image.get_name(), r_lev)

            # Get appropriately scaled ROI for the given dimension.
            resolution_dimensions = input_image.image_dimensions()[r_lev]
            segment = image_segmentation.get_scaled_segments(resolution_dimensions[1], resolution_dimensions[0])[
                box_index]

            # Use all z, c & t planes of the image.
            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)

            # image data with dimensions [c,x,y,z,t]
            image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                        t=[0, t],
                                                                        c=[0, c],
                                                                        z=[0, z],
                                                                        y=[segment[1], segment[3]],
                                                                        x=[segment[0], segment[2]])

            # Saves the image as a single RGB TIFF.
            if TIFFImageCropper.save_image(image_data, resolution_output_filename):
                single_resolution_image_paths.append(resolution_output_filename)

        # Create multipage TIFF image from those created above.
        TIFFImageCropper.combine_resolutions("{}/{}_full.tiff".format(output_folder, input_image.get_name()),
                                             single_resolution_image_paths)
        logging.info("Finished saving image %d from %s.", box_index, input_path)

    @staticmethod
    def combine_resolutions(combined_image_path, image_paths_list):
        """
        Creates a Multi-paged TIFF file from the fiven image list. 
        :param combined_image_path: File path to new Multi-page TIFF. Assumed to be valid
        :param image_paths_list: List of file paths to create the multi-page tiff with. Assumed to be both a valid 
                                 filepath and a TIFF extension. 
        """
        with TIFF(combined_image_path, True) as tf:
            for tiff_path in image_paths_list:
                try:
                    im = Image.open(tiff_path)
                    im.save(tf)
                    tf.newFrame()
                    im.close()
                except Exception as e:
                    logging.info("Could not create multi-page TIFF. Couldn't compile file: %s", tiff_path)

    @staticmethod
    def save_image(image_data, output_filename):
        """
        Saves all channels of an image into a RGB 2D image in TIFF Format. 
        :param image_data: Euclidean data in form [x,y,z,c,t]
        :param output_filename: Filename to save to. Assumed to be valid. 
        @:return: True if image successfully saved. 
        """

        try:
            im = Image.fromarray(image_data[:, :, 0, :, 0],
                                 mode="RGB")  # Ignore time and Z planes, create RGB plan image
        except Exception as e:
            logging.error("Error occured when transforming numpy data to image. Meant to output to: %s. \n"
                          "image data is of dimensions %s and size %d", e, image_data.shape, image_data.size)
            return False
        im.save(output_filename, "TIFF")
        im.close()
        return True

    @staticmethod
    def save_image_2(output_filename, image_data):
        """
        Deprecetated Tiff saving method. Tifffile iterates through first dimension (in our case x) and saves one at a
        time. Obviously this cannot work with the image sizes in question. 
        """
        tifffile.imsave(output_filename, data=image_data, append=False, bigtiff=True, software="SlideCrop 2")
