# SlideCrop
An automated microscope slide cropping application for various types of file formats (primarily .ims extensions). Provides automatic segmentation of separate regions of interest in an image and produces a series of segmented images over the original image's channel, time and z planes. 

## Getting Started
### Dependencies
SlideCrop has the following dependencies: 
* Numpy
* Scipy
* H5py
* Skimage
* PIL (pillow) 

## Development
Notes for future development. Wiki pages for more detailed notes. 

### InputImage Interface
Interface for image extensions for microscope slides that can be segmented and cropped. Currently only supporting .ims extensions. 

### ImageCropper Interface
Interface for producing output segmented images. Specifies an implementation for producing specific output extensions. Currently only supporting .tiff extensions. 

### ImageSegmenter Class
Implementation of the current algorithm to identify regions of interest and produce a series of bounding boxes for their cropping. 




