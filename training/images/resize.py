import opencv.image_manipulations as im
import os
import cv2

# Set the input and output directories
cwd = os.getcwd()
input_directory = os.path.join(cwd, 'original')
output_directory = os.path.join(cwd, 'resized')

# Set the desired new dimensions
width = 640
height = 640
interpolation_method = cv2.INTER_AREA

# Resize images
im.resize_image(input_directory, output_directory, width, height, interpolation_method)

