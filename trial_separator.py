import numpy as np
import h5py
import matplotlib
import os
from math import ceil

FILEPATH = "C:/Users/uqjeadi2/Downloads/NG_GAD67_GFP16-B.ims"

def main():
    ##  Load File and get lowest Level resolution of IMS file
    IMS_file = h5py.File(FILEPATH)
    file_data= IMS_file.get("/DataSet/ResolutionLevel 7/TimePoint 0/Channel 0/Data")
    lowest_data_level_image = file_data[0]
    image_width = len(lowest_data_level_image[0])

    ##  image_size = image_width*image_height
    ##  image_height = image_size/image_width
    image_height = file_data.size/ image_width
    rows_per_horizontal_check = 1 #ceil(image_height)
    row_number = 0;
    horizontal_transition_points = {}
    for row in lowest_data_level_image[::rows_per_horizontal_check]:
        horizontal_transition_points[row_number] = find_horizontal_transition_points(row)
        if len(horizontal_transition_points[row_number]) ==0:
            print(row_number)
        row_number += rows_per_horizontal_check

    print(image_height)
    print(image_width)
    print(file_data.size)
    print(rows_per_horizontal_check)
    print(horizontal_transition_points)

def find_horizontal_transition_points(row):
    currently_zero = True if row[0] ==0 else False
    transition_points = []
    for i in range(len(row)-1):
        if currently_zero:
           if row[i+1] != 0:
               transition_points.append(i+1)
               currently_zero = False
        else:
            if row[i+1] == 0:
                transition_points.append(i)
                currently_zero = True
    return transition_points

if __name__ == '__main__':
    main()