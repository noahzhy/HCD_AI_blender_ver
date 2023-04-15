import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont


# function to split the image path
def split_path(path):
    # split the path to get the image name
    head, tail = os.path.split(path)
    # split the image name to get the image despription
    name, ext = os.path.splitext(tail)
    # split the image description to type description and image number
    _type, num = name.split('_')[0], name.split('_')[1]
    return _type, num


# function to show the image
# given the image path, split the path to get the image type and number
# find the mask file with the same number
# show mask and image together
def show(path):
    _type, num = split_path(path)
    # find the mask file with the same number
    mask_path = glob.glob("data/body_" + num + '*.png')[0]
    # read the image and mask
    img = Image.open(path)
    mask = Image.open(mask_path)
    # show the image and mask together
    plt.figure()
    plt.subplot(1, 2, 1)
    plt.imshow(img)
    plt.subplot(1, 2, 2)
    plt.imshow(mask)
    plt.show()



if __name__ == "__main__":
    _list = glob.glob("data/img_*.png")
    # randomly sort the image list
    np.random.shuffle(_list)
    for i in _list:
        print(i)
        show(path=i)
        break
