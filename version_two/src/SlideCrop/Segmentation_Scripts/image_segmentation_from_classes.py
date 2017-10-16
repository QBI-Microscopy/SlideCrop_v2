import version_two.src.SlideCrop.ImarisImage as I
from version_two.src.SlideCrop.ImageSegmenter import ImageSegmenter as seg
from version_two.src.SlideCrop.TIFFImageCropper import TIFFImageCropper

FILE = "E:/testdata2/170818_APP_1878 UII_BF~B.ims"
image = I.ImarisImage(FILE)

channelled_image = image.get_multichannel_segmentation_image()

segmentations = seg.segment_image(channelled_image)
#
# for i in segmentations.segments:
#     print(i)

TIFFImageCropper.crop_input_images(image, segmentations, "E:/FirstTest")


