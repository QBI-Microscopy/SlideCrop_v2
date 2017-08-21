import scipy.ndimage as nd
import numpy as np
import matplotlib.pyplot as plt


image = nd.imread("E:/download.jpg")
x_dim_image_edge = image.shape[0]
y_dim_image_edge = image.shape[1]
# mean intensity for each channel
# Averaged across axis separately. Shape = (x,y,3) -> (x -> 3) -> (1,3)
channel_mean_vector  = np.mean(np.mean(image, axis =1),axis =0 )

# Create a image vector with pixel values from the 2D corners of all channels. Used as a background intensity mean.
background_vector = np.zeros((4,4,3))
background_vector[0:2, 0:2, 3] = image[0:2, 0:2, 3]
background_vector[0:2, 2:4, 3] = image[0:2, y_dim_image_edge-2:y_dim_image_edge, 3]
background_vector[2:4, 0:2, 3] = image[x_dim_image_edge-2:x_dim_image_edge, 0:2, 3]
background_vector[2:4, 2:4, 3] = image[x_dim_image_edge-2:x_dim_image_edge, y_dim_image_edge-2:y_dim_image_edge, 3]
background_channel_mean_vector = np.mean(np.mean(background_vector, axis =1),axis =0 )

#Choose channel for clustering based on maximum background-average intensity difference.
max_difference_channel = np.abs(background_channel_mean_vector - channel_mean_vector)
clustering_channel = np.argmax(max_difference_channel)
channel_image = image[clustering_channel]

# Set initial background, Ub and foreground Uo  intensity means as averages previously found.
Ub = background_channel_mean_vector[clustering_channel]
Uo = channel_mean_vector[clustering_channel]


#
for i in range(10):

    Ub_temp = np.mean(channel_image[np.where(channel_image < (Uo+Ub/2))])
    Uo_temp = np.mean(channel_image[np.where(channel_image > (Uo+Ub/2))])
    Ub = Ub_temp
    Uo = Uo_temp

