import version_two.src.SlideCrop.ImarisImage as I
from version_two.src.SlideCrop.ImageSegmenter import ImageSegmenter as seg

FILE = "E:/questionable_testdata/170818_APP_1926_UII+O2_BF~B.ims"
image = I.ImarisImage(FILE)

channelled_image = image.get_multichannel_segmentation_image()

segmentations = seg.segment_image(channelled_image)

for i in segmentations.segments:
    print(i)


