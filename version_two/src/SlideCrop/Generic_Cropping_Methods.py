from multiprocessing import Process

import version_two.src.SlideCrop.ImarisImage as I
from version_two.src.SlideCrop.ImageSegmenter import ImageSegmenter as seg
from version_two.src.SlideCrop.TIFFImageCropper import TIFFImageCropper
from version_two.src.SlideCrop.InputImage import InputImage
import os

def crop_all_in_folder(folder_path, output_path, concurrent = False):
    """
    Handler to crop all images in a given folder. Will ignore non-compatible file types 
    :param folder_path: Path to the files wanted to be 
    :param output_path: Folder path to create all new folders and images in. 
    :param concurrent: Whether to multiprocess each file. (Current has not been tested) 
    :return: 
    """
    if concurrent:
        pid_list = []

    for filename in os.listdir(folder_path):
        file_path = "{}/{}".format(folder_path, filename)
        if concurrent:
            pid_list.append(spawn_crop_process(file_path, output_path))
        else:
            crop_single_image(file_path, output_path)

    if concurrent:
        for proc in pid_list:
            proc.join()

def spawn_crop_process(file_path, output_path):
    """
    Handles creating and starting a new process to crop an individual file. 
    :param file_path: Tpo
    :param output_path: 
    :return: 
    """
    cropper = Process(target=crop_single_image, args=(file_path, output_path))
    cropper.start()
    return cropper


def crop_single_image(file_path, output_path):
    """
    Encapsulation method for cropping an individual image.
    :param file_path: String path to the desired file. Assumed to be .ims extension
    :param output_path: 
    :return: 
    """
    ext_check = InputImage.get_extension(file_path)
    if ext_check != "ims":
        raise TypeError("{} is currently not a supported file type".format(ext_check))

    image = I.ImarisImage(file_path)
    channelled_image = image.get_multichannel_segmentation_image()
    image.close_file()

    segmentations = seg.segment_image(channelled_image)

    TIFFImageCropper.crop_input_images(file_path, segmentations, output_path)



if __name__ == '__main__':
    crop_all_in_folder("E:/testdata1", "E:/FirstTest", concurrent=False)