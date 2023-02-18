import os
import sys
import glob

from PIL import Image, ImageDraw
import numpy as np
# parser xml
import xml.etree.ElementTree as ET


# parser xml file to get the bbox node via given xml file path
def get_bbox_from_xml(xml_path):
    bbox = []
    # the xml file format is like the above
    tree = ET.parse(xml_path)
    root = tree.getroot()

    bbox = root.find("object").find("bndbox")
    # parse xmin, ymin, xmax, ymax node
    xmin = float(bbox.find("xmin").text)
    ymin = float(bbox.find("ymin").text)
    xmax = float(bbox.find("xmax").text)
    ymax = float(bbox.find("ymax").text)
    # return the bbox
    bbox = [[xmin, ymin], [xmax, ymax]]

    # get file base name
    file_name = os.path.basename(xml_path)
    # match the image file name
    img_path = os.path.join("data", file_name.replace("xml", "png"))
    # read image via PIL
    img = Image.open(img_path).convert("RGB")
    # draw the keypoints
    draw = ImageDraw.Draw(img)
    # draw the bbox
    bbox = np.array(bbox) * np.array([img.width, img.height]).astype(np.int32)
    bbox = [tuple(bbox[0]), tuple(bbox[1])]
    draw.rectangle(bbox, outline="green", width=2)

    # show the image
    img.show()


if __name__ == "__main__":
    # get all xml file path in the given folder
    xml_dir = "data"
    xml_paths = glob.glob(os.path.join(xml_dir, "*.xml"))
    # sort the xml file path via create time
    xml_paths.sort(key=os.path.getctime, reverse=True)
    pose = get_bbox_from_xml(xml_paths[0])
