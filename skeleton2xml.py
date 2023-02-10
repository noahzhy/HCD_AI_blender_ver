# scrpt to generate xml file from skeleton keypoints array
import os
import glob
import json
import datetime
import xml.etree.ElementTree as ET
from collections import defaultdict

import cv2
import numpy as np
from PIL import Image, ImageDraw


class Person():
    def __init__(self, name, bbox, pose, hand):
        self.name = name
        self.bbox = bbox
        self.pose = pose
        self.hand = hand

    def get_xml(self):
        xml_txt = """<object>\n"""
        xml_txt += """<name>""" + self.name + """</name>\n"""
        xml_txt += """<pose>Unspecified</pose>\n"""
        xml_txt += """<truncated>0</truncated>\n"""
        xml_txt += """<difficult>0</difficult>\n"""
        xml_txt += get_bbox(self.bbox)
        xml_txt += get_pose(self.pose)
        xml_txt += get_pose(self.hand)
        xml_txt += """</object>\n"""
        return xml_txt

    def get_dict(self):
        return {
            "name": self.name,
            "bbox": self.bbox,
            "pose": self.pose,
            "hand": self.hand
        }


def get_bbox(bbox):
    xmin = bbox[0][0]
    ymin = bbox[0][1]
    xmax = bbox[1][0]
    ymax = bbox[1][1]
    xml_txt = """<bndbox>\n"""
    xml_txt += """<xmin>""" + str(xmin) + """</xmin>\n"""
    xml_txt += """<ymin>""" + str(ymin) + """</ymin>\n"""
    xml_txt += """<xmax>""" + str(xmax) + """</xmax>\n"""
    xml_txt += """<ymax>""" + str(ymax) + """</ymax>\n"""
    xml_txt += """</bndbox>\n"""
    return xml_txt


def get_pose(keypoints):
    xml_txt = """<keypoints>\n"""
    for key, value in keypoints.items():
        xml_txt += """<""" + key + """>"""
        xml_txt += """<x>""" + str(value[0]) + """</x>\n"""
        xml_txt += """<y>""" + str(value[1]) + """</y>\n"""

        if (value[0] > 0 and value[0] < 1) and (value[1] > 0 and value[1] < 1):
            xml_txt += """<v>1</v>\n"""
        else:
            xml_txt += """<v>0</v>\n"""

        xml_txt += """</""" + key + """>\n"""
    xml_txt += """</keypoints>\n"""
    return xml_txt


def get_object(obj_dict):
    xml_txt = """<object>\n"""
    xml_txt += """<name>""" + obj_dict["name"] + """</name>\n"""
    xml_txt += """<pose>Unspecified</pose>\n"""
    xml_txt += """<truncated>0</truncated>\n"""
    xml_txt += """<difficult>0</difficult>\n"""
    xml_txt += get_bbox(obj_dict["bbox"])
    xml_txt += get_pose(obj_dict["keypoints"])
    xml_txt += """</object>\n"""
    return xml_txt


# function to generate xml file
def generate_xml(img_path):
    # img_path = "images/000000000001.jpg"
    # img_name = "000000000001.jpg"
    img_name = os.path.basename(img_path)
    img = Image.open(img_path)
    img_width, img_height = img.size
    # get image channel number by pillow
    img_channel = len(img.getbands())
    xml_txt = """"""  # xml file text
    xml_txt += """<?xml version="1.0" encoding="UTF-8"?>\n"""
    xml_txt += """<annotation>\n"""
    xml_txt += """<folder>images</folder>\n"""
    xml_txt += """<filename>""" + img_name + """</filename>\n"""
    xml_txt += """<path>""" + img_path + """</path>\n"""
    xml_txt += """<source>\n"""
    xml_txt += """<database>Unknown</database>\n"""
    xml_txt += """</source>\n"""
    xml_txt += """<size>\n"""
    xml_txt += """<width>""" + str(img_width) + """</width>\n"""
    xml_txt += """<height>""" + str(img_height) + """</height>\n"""
    xml_txt += """<depth>""" + str(img_channel) + """</depth>\n"""
    xml_txt += """</size>\n"""
    xml_txt += """<segmented>0</segmented>\n"""

    # add object
    for obj in objects:
        xml_txt += get_object(obj)

    xml_txt += """</annotation>\n"""
    return xml_txt



