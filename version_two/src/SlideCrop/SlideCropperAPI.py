from multiprocessing import Process
import logging
import version_two.src.SlideCrop.ImarisImage as I
from version_two.src.SlideCrop.ImageSegmenter import ImageSegmenter
from version_two.src.SlideCrop.TIFFImageCropper import TIFFImageCropper
from version_two.src.SlideCrop.InputImage import InputImage
import os

DEFAULT_LOGGING_FILEPATH = "E:/SlideCropperLog.txt"
FORMAT = '|%(thread)d |%(filename)s |%(funcName)s |%(lineno)d ||%(message)s||'
class SlideCropperAPI(object):
    """
    Main Class for using SlideCropper functionality. All methods are class method based.     
    """

    @classmethod
    def crop_all_in_folder(cls, folder_path, output_path, concurrent = False):
        """
        Handler to crop all images in a given folder. Will ignore non-compatible file types 
        :param folder_path: Path to the files wanted to be 
        :param output_path: Folder path to create all new folders and images in. 
        :param concurrent: Whether to multiprocess each file. (Current has not been tested) 
        """
        if concurrent:
            pid_list = []

        for filename in os.listdir(folder_path):
            file_path = "{}/{}".format(folder_path, filename)
            if concurrent:
                pid_list.append(SlideCropperAPI.spawn_crop_process(file_path, output_path))
            else:
                SlideCropperAPI.crop_single_image(file_path, output_path)

        if concurrent:
            for proc in pid_list:
                proc.join()

    @classmethod
    def spawn_crop_process(cls, file_path, output_path):
        """
        Handles creating and starting a new process to crop an individual file. 
        :param file_path: Tpo
        :param output_path: 
        :return: 
        """
        cropper = Process(target=SlideCropperAPI.crop_single_image, args=(file_path, output_path))
        cropper.start()
        return cropper

    @classmethod
    def crop_single_image(cls, file_path, output_path):
        """
        Encapsulation method for cropping an individual image.
        :param file_path: String path to the desired file. Assumed to be .ims extension
        :param output_path: 
        :return: 
        """
        logging.info("Starting to crop: {0}".format(file_path))
        ext_check = InputImage.get_extension(file_path)
        if ext_check != "ims":
            raise TypeError("{} is currently not a supported file type".format(ext_check))


        image = I.ImarisImage(file_path)
        segmentations = ImageSegmenter.segment_image(image.get_multichannel_segmentation_image())
        image.close_file()
        logging.info("Finished Segmenting of image: starting crop.")
        TIFFImageCropper.crop_input_images(file_path, segmentations, output_path)
        logging.info("Finished Cropping of image.")

def crop_all_from(cls, file_path_list, output_path, concurrent = False):
    """
    Handler to crop all images in a given list. Will ignore non-compatible file types 
    :param folder_path: Path to the files wanted to be 
    :param output_path: Folder path to create all new folders and images in. 
    :param concurrent: Whether to multiprocess each file. (Current has not been tested) 
    """
    if concurrent:
        pid_list = []

    for file_path in file_path_list:
        if concurrent:
            pid_list.append(SlideCropperAPI.spawn_crop_process(file_path, output_path))
        else:
            SlideCropperAPI.crop_single_image(file_path, output_path)

    if concurrent:
        for proc in pid_list:
            proc.join()

def main():
    """
    Standard wrapper for API usage. Sets API up to call innerMain function. 
    """
    logging.basicConfig(filename="E:/SlideCropperLog.txt", level= logging.DEBUG, format= FORMAT)
    logging.captureWarnings(True)

    parent_pid = os.getpid()
    # Only log for first process created. Must check that process is the original.
    if os.getpid() == parent_pid:
        logging.info("\nSlideCropper started with pid: {}".format(os.getpid()))
    innerMain()
    if os.getpid() == parent_pid:
        logging.info("SlideCropper ended with pid: {}\n".format(os.getpid()))

def innerMain():
    """
    API actions in use. 
    """

    SlideCropperAPI.crop_all_in_folder("E:/testdata1", "E:/18_02_20")

if __name__ == '__main__':
    main()