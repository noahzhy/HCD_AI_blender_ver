import os
import glob
import json
import datetime
import xml.etree.ElementTree as ET
from collections import defaultdict

import numpy as np


class Person():
    def __init__(self, bbox, pose, hand):
        self.name = 'person'
        self.bbox = bbox
        self.pose = pose
        self.hand = hand

    def get_xml(self):
        xml_txt = """\t<object>\n"""
        xml_txt += """\t\t<name>""" + str(self.name) + """</name>\n"""
        xml_txt += """\t\t<pose>Unspecified</pose>\n"""
        x1, y1, x2, y2 = self.bbox
        if is_visible(x1, y1) and is_visible(x2, y2):
            xml_txt += """\t\t<truncated>0</truncated>\n"""
        else:
            xml_txt += """\t\t<truncated>1</truncated>\n"""
        xml_txt += """\t\t<difficult>0</difficult>\n"""
        xml_txt += bbox2xml(self.bbox)
        xml_txt += pose2xml(self.pose, "body")
        xml_txt += pose2xml(self.hand, "hand")
        xml_txt += """\t</object>\n"""
        return xml_txt

    def get_dict(self):
        return {
            "name": self.name,
            "bbox": self.bbox,
            "pose": self.pose,
            "hand": self.hand,
        }


def is_visible(x, y) -> bool:
    if (x > 0 and x < 1) and (y > 0 and y < 1):
        return True
    else:
        return False


# function to convert bbox to xml
def bbox2xml(bbox):
    # clamp bbox
    xmin = max(0, bbox[0])
    ymin = max(0, bbox[1])
    xmax = min(1, bbox[2])
    ymax = min(1, bbox[3])
    # convert to xml
    xml_txt = """\t\t<bndbox>\n"""
    xml_txt += """\t\t\t<xmin>""" + str(xmin) + """</xmin>\n"""
    xml_txt += """\t\t\t<xmax>""" + str(xmax) + """</xmax>\n"""
    xml_txt += """\t\t\t<ymin>""" + str(ymin) + """</ymin>\n"""
    xml_txt += """\t\t\t<ymax>""" + str(ymax) + """</ymax>\n"""
    xml_txt += """\t\t</bndbox>\n"""
    return xml_txt


# function to convert pose to xml
def pose2xml(keypoints, label_name:str):
    xml_txt = """\t\t<{}>\n""".format(label_name)
    for key, value in keypoints.items():
        x, y, is_occluded = value

        xml_txt += """\t\t\t<""" + key + """>\n"""
        xml_txt += """\t\t\t\t<x>""" + str(x) + """</x>\n"""
        xml_txt += """\t\t\t\t<y>""" + str(y) + """</y>\n"""

        if is_visible(x, y):
            xml_txt += """\t\t\t\t<v>1</v>\n"""
        else:
            xml_txt += """\t\t\t\t<v>0</v>\n"""

        xml_txt += """\t\t\t\t<occluded>""" + str(is_occluded) + """</occluded>\n"""

        xml_txt += """\t\t\t</""" + key + """>\n"""
    xml_txt += """\t\t</{}>\n""".format(label_name)
    return xml_txt


# function to generate xml file
def save_xml(objects:list, img_path:str, xml_path:str, img_width:int, img_height:int, img_channel:int):
    img_name = os.path.basename(img_path)
    xml_txt = """"""  # xml file text
    xml_txt += """<?xml version="1.0" encoding="UTF-8"?>\n"""
    xml_txt += """<annotation>\n"""
    xml_txt += """\t<folder>images</folder>\n"""
    xml_txt += """\t<filename>""" + img_name + """</filename>\n"""
    xml_txt += """\t<path>""" + img_path + """</path>\n"""
    xml_txt += """\t<source>\n"""
    xml_txt += """\t\t<database>Unknown</database>\n"""
    xml_txt += """\t</source>\n"""
    xml_txt += """\t<size>\n"""
    xml_txt += """\t\t<width>""" + str(img_width) + """</width>\n"""
    xml_txt += """\t\t<height>""" + str(img_height) + """</height>\n"""
    xml_txt += """\t\t<depth>""" + str(img_channel) + """</depth>\n"""
    xml_txt += """\t</size>\n"""
    xml_txt += """\t<segmented>0</segmented>\n"""

    # add object
    for obj in objects:
        xml_txt += obj.get_xml()

    xml_txt += """</annotation>\n"""
    
    # save xml file
    xml_name = os.path.splitext(img_name)[0] + ".xml"
    xml_file = os.path.join(xml_path, xml_name)
    with open(xml_file, "w") as f:
        f.write(xml_txt)
