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

from multiprocessing import Process
import version_two.src.SlideCrop.ImarisImage as I

#  TODO: need to encode bigtiff requirement (in progress)
#  TODO: repackage tiff resolutions into single image with ability to retrieve them
#  TODO: look into time bottlenecks.
#  TODO: consider compression



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


        pid_list = []

        ## Iterate through each bounding box
        for box_index in range(len(image_segmentation.segments)):
            crop_process = Process(target=TIFFImageCropper.crop_single_image, args=(input_path, image_segmentation, output_path, box_index))
            pid_list.append(crop_process)
            crop_process.start()
            # crop_process.join()
        #
        for proc in pid_list:
            proc.join()
            # TIFFImageCropper.crop_single_image(input_image, image_segmentation, output_path, box_index)
        #
        # for pid in pid_list:
        #     Process.

    @staticmethod
    #  TODO: check with Liz the format wanted...
    def crop_single_image(input_path, image_segmentation, output_path, box_index):
        print("in single process")
        ## Create New, empty Tiff file.
        # output_filename  = "{}/{}_{}.tif".format(output_path, input_image.get_name(), box_index)
        input_image = I.ImarisImage(input_path)

        output_folder = "{}/ind{}".format(output_path, box_index)
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)

        photo_list = []


        for r_lev in range(input_image.get_resolution_levels()):
            output_filename = "{}/{}_{}.tiff".format(output_folder, input_image.get_name(), r_lev)
            photo_list.append(output_filename)
            ## Create a 3dim image to include all the channels (do we want times as fourth dimension)
            resolution_dimensions = input_image.image_dimensions()[r_lev]
            segment = image_segmentation.get_scaled_segments(resolution_dimensions[0], resolution_dimensions[1])[
                box_index]

            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)

            # image data with dimensions [c,x,y,z,t]
            image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                        t=[0, t],
                                                                        c=[0, c],
                                                                        z=[0, z],
                                                                        y=[segment[1], segment[3]],
                                                                        x=[segment[0], segment[2]])
            print(image_data.shape)
            print("r = {}, box = {}".format(r_lev, box_index))
            print("resolution  {} area {}".format(resolution_dimensions, segment))
            print("for found boxes at 3000x1200 and box {}".format(image_segmentation.segments[box_index]))
            print(image_data.nbytes > 2**32-2**25)
            ## Append to existing file on all resolutions except resolution = 0
            # to_append = r_lev != 0
            # print(image_data.dtype)
            # # savefile.seek(r_lev, os.SEEK_SET)
            TIFFImageCropper.save_image_1(image_data, output_filename)
            # TIFFImageCropper.save_image_2(output_filename, image_data)
            # im = Image.fromarray(image_data[:,:,0,:,0], mode = "RGB")
            # im.save(output_filename, "TIFF")
            # im.close()
            # TIFFPlugin._save(Image.fromarray(image_data.astype(np.uint), mode = "L"), savefile)
            # # savefile.write(np.ascontiguousarray(image_data))
            # savefile.newFrame()

            # tifffile.imsave(output_filename, data = image_data, append = False, bigtiff = True, software="SlideCrop 2")
            print("Done\n")
            ## clear memory by removing as many variables as possible

        # savefile.close()

        with TIFF("{}/{}_full.tiff".format(output_folder, input_image.get_name()), True) as tf:
            for tiff_path in photo_list:
                try:
                    im = Image.open(tiff_path)
                    im.save(tf)
                    tf.newFrame()
                    im.close()
                except Exception as e:
                    print(e.with_traceback())

    @staticmethod
    def save_image_1(image_data, output_filename):
        im = Image.fromarray(image_data[:, :, 0, :, 0], mode="RGB")
        im.save(output_filename, "TIFF")
        im.close()

    @staticmethod
    def save_image_2(output_filename, image_data):
        tifffile.imsave(output_filename, data = image_data, append = False, bigtiff = True, software="SlideCrop 2")
