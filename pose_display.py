import os
import sys
import glob

from PIL import Image, ImageDraw
import numpy as np
# parser xml
import xml.etree.ElementTree as ET


# parser xml file to get the keypoints node via given xml file path
def get_pose_from_xml(xml_path):
    body = []
    hand = []
    # the xml file format is like the above
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # get the keypoints node
    pose = root.find("object").find("body")
    for pose in pose:
        body.append([float(pose.find("x").text), float(pose.find("y").text)])
    # return pose

    pose = root.find("object").find("hand")
    for pose in pose:
        hand.append([float(pose.find("x").text), float(pose.find("y").text)])

    # get file base name
    file_name = os.path.basename(xml_path)
    # match the image file name
    img_path = os.path.join("data", file_name.replace("xml", "png"))
    # read image via PIL
    img = Image.open(img_path).convert("RGB")
    # draw the keypoints
    draw = ImageDraw.Draw(img)
    for point in body:
        x, y = point
        point = (x * 512, y * 512)
        draw.ellipse((point[0] - 5, point[1] - 5, point[0] + 5, point[1] + 5), fill=(255, 0, 0))

    for point in hand:
        x, y = point
        point = (x * 512, y * 512)
        draw.ellipse((point[0] - 2, point[1] - 2, point[0] + 2, point[1] + 2), fill=(0, 255, 0))

    # show the image
    img.show()


if __name__ == "__main__":
    # get all xml file path in the given folder
    xml_dir = "data"
    xml_paths = glob.glob(os.path.join(xml_dir, "*.xml"))
    pose = get_pose_from_xml(xml_paths[0])
