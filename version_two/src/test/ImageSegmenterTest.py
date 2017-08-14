from version_two.src.SlideCrop.ImageSegmenter import ImageSegmenter as ImageSegmenter
from version_two.src.SlideCrop.ImarisImage import ImarisImage as ImarisImage
from version_two.src.SlideCrop.ImageSegmentation import ImageSegmentation as ImageSegmentation
import unittest
from operator import itemgetter
TESTFILE1 = "E:/testfile.ims"
MAXIMUM_ERROR = 1.1 # i.e 10% greater
class ImageSegmenterTest(unittest.TestCase):
    """
    Test Suite for ImageSegmenter
    """

    def test_segment_image(self):
        self.assertTrue(self.segment_and_test(TESTFILE1), "Successfully cropped TESTFILE1")

    def segment_and_test(self, file_path):
        image = ImarisImage(file_path)
        segmentations = ImageSegmenter.segment_image(image.get_segment_res_image())
        return self.compare_segmentations(segmentations.get_scaled_segments(1000, 1000),
                                          self.correct_testfile_one_segment().
                                          get_scaled_segments(1000, 1000))


    def compare_segmentations(self, test_segment, correct_segment):
         if(len(test_segment) != len(correct_segment)):
             return False

         # sort test_segment to improve read times.
         test_segment = sorted(test_segment, key=itemgetter(0,2,1,3))
         for test_seg, correct_seg in test_segment, correct_segment:
             ## Must check first two points test_(x1, y1) < correct_(x1, y1) &&
             ##                             test_(x2, y2) > correct_(x1, y1)
             ##  i.e the two test segment points are outside the minimum rectangle defined by correct_segment
             if not self.compare_segment(test_seg, correct_seg):
                 return False

         return True

    def compare_segment(self, test_seg, correct_seg):
        return True


    def correct_testfile_one_segment(self):
        """
        Returns an imageSegmentation object with the minimum size rectangles that TESTFILE1 can have. 
        Segments inside these bounds are too tight for the segmentation. 
        """
        return ImageSegmentation(1,1)
