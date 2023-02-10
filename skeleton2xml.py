# scrpt to generate xml file from skeleton keypoints array
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
        xml_txt = """<object>\n"""
        xml_txt += """\t<name>""" + str(self.name) + """</name>\n"""
        xml_txt += """\t<pose>Unspecified</pose>\n"""
        xml_txt += """\t<truncated>0</truncated>\n"""
        xml_txt += """\t<difficult>0</difficult>\n"""
        xml_txt += bbox2xml(self.bbox)
        xml_txt += pose2xml(self.pose, isPose=True)
        xml_txt += pose2xml(self.hand, isPose=False)
        xml_txt += """</object>\n"""
        return xml_txt

    def get_dict(self):
        return {
            "name": self.name,
            "bbox": self.bbox,
            "pose": self.pose,
            "hand": self.hand
        }


# function to convert bbox to xml
def bbox2xml(bbox):
    xmin = bbox[0]
    ymin = bbox[1]
    xmax = bbox[2]
    ymax = bbox[3]
    xml_txt = """<bndbox>\n"""
    xml_txt += """\t<xmin>""" + str(xmin) + """</xmin>\n"""
    xml_txt += """\t<ymin>""" + str(ymin) + """</ymin>\n"""
    xml_txt += """\t<xmax>""" + str(xmax) + """</xmax>\n"""
    xml_txt += """\t<ymax>""" + str(ymax) + """</ymax>\n"""
    xml_txt += """</bndbox>\n"""
    return xml_txt


# function to convert pose to xml
def pose2xml(keypoints, isPose:bool=True):
    xml_txt = """<pose>\n""" if isPose else """<hand>\n"""
    for key, value in keypoints.items():
        xml_txt += """\t<""" + key + """>\n"""
        xml_txt += """\t\t<x>""" + str(value[0]) + """</x>\n"""
        xml_txt += """\t\t<y>""" + str(value[1]) + """</y>\n"""

        if (value[0] > 0 and value[0] < 1) and (value[1] > 0 and value[1] < 1):
            xml_txt += """\t\t<v>1</v>\n"""
        else:
            xml_txt += """\t\t<v>0</v>\n""" 

        xml_txt += """\t</""" + key + """>\n"""
    xml_txt += """</pose>\n""" if isPose else """</hand>\n"""
    return xml_txt


# function to generate xml file
def save_xml(objects:list, img_path:str, xml_path:str, img_width:int, img_height:int, img_channel:int):
    # img_path = "images/000000000001.jpg"
    # img_name = "000000000001.jpg"
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

