#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 13 20:35:00 2018

@author: andriylevitskyy
"""
import os

from PIL import Image, ImageEnhance, ImageFilter, ImageChops
from io import BytesIO
import cv2
import numpy
def binarize_image(image_file, threshold):
    """Binarize an image."""
    image = image_file.convert('L')  # convert image to monochrome
    image = numpy.array(image)
    image = binarize_array(image, threshold)
    return(image)


def binarize_array(numpy_array, threshold=200):
    """Binarize a numpy array."""
    for i in range(len(numpy_array)):
        for j in range(len(numpy_array[0])):
            if numpy_array[i][j] > threshold:
                numpy_array[i][j] = 255
            else:
                numpy_array[i][j] = 0
    return numpy_array
def change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))
    def contrast(c):
        return 128 + factor * (c - 128)
    return img.point(contrast)
def change_color(acktorgb,substitute):
    im=Image.fromarray(acktorgb)
    data = numpy.array(im)   # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T # Temporarily unpack the bands for readability

# Replace white with red... (leaves alpha values alone...)
    white_areas = (red == 255) & (blue == 255) & (green == 255)
    black_areas= (red == 0) & (blue == 0) & (green == 0)
    data[..., :][white_areas.T] = (255, 255, 255,0) # Transpose back needed
    data[..., :][black_areas.T] = substitute
    im2 = Image.fromarray(data)
    return im2
color_codes=[(0,0,0,255),(255,0,0,255),(255,127,0,255),(255,255,0,255),(0,255,0,255),
             (0,0,255,255),(75,0,130,255),(148,0,211,255)]
for i in range(1,101):
    print(i)
    path="image_part_"
    if i <10:
        path=path+"00"+str(i)+".jpg"
    elif i<100 :
        path=path+"0"+str(i)+".jpg"
    else:
        path=path+str(i)+".jpg"
    for color_code in range(1,9):
        path_save="image"+str(i+100*color_code)+".png"
        color=color_codes[color_code-1]
        image=Image.open(path)
        array=binarize_image(image,200)
        bw=Image.fromarray(binarize_image(image,200))   
        acktorgb = cv2.cvtColor(array,cv2.COLOR_GRAY2RGBA)
        im2=change_color(acktorgb,color)
        im2.save(path_save)