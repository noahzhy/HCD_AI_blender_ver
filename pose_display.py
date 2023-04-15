import os
import sys
import glob

from PIL import Image, ImageDraw
import numpy as np
# parser xml
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt


# parser xml file to get the keypoints node via given xml file path
def get_pose_from_xml(xml_path):
    body = []
    hand = []
    # the xml file format is like the above
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # get the keypoints node
    poses = root.find("object").find("body")
    for pose in poses:
        if int(pose.find("occluded").text) == 0:
            body.append([float(pose.find("x").text), float(pose.find("y").text), pose.tag])
    # return pose

    poses = root.find("object").find("hand")
    for pose in poses:
        if int(pose.find("occluded").text) == 0:
            hand.append([float(pose.find("x").text), float(pose.find("y").text), pose.tag])

    # get file base name
    file_name = os.path.basename(xml_path)
    # match the image file name
    img_path = os.path.join("data", file_name.replace("xml", "png"))

    # create a new figure
    fig = plt.figure()
    # 1 row, 3 columns
    # read image via PIL
    img = Image.open(img_path).convert("RGB")
    # load the image
    img_src = np.array(img)
    # show the image
    plt.subplot(1, 3, 1)
    plt.imshow(img_src)
    # draw the keypoints
    draw = ImageDraw.Draw(img)
    img_copy = img.copy()
    draw_text = ImageDraw.Draw(img_copy)

    for point in hand:
        x, y, label = point
        point = (x * 512, y * 512)
        draw.ellipse((point[0] - 2, point[1] - 2, point[0] + 2, point[1] + 2), fill=(0, 255, 0))
        draw_text.ellipse((point[0] - 2, point[1] - 2, point[0] + 2, point[1] + 2), fill=(0, 255, 0))

        keep_label = ["wrist", "thumb", "index", "middle", "ring", "pinky"]
        # label convert to lower case
        label = label.lower()
        # if label include the keep_label, then draw the label
        if any([label.find(k) != -1 for k in keep_label]):
            label = label.replace("lefthand", "").replace("righthand", "") 
            # replace the label in the keep_label to keep first letter
            for k in keep_label: label = label.replace(k, k[0])
            # label color is white
            draw_text.text((point[0] + 5, point[1] + 5), label, fill=(255, 255, 255))
        else:
            draw_text.text((point[0] + 5, point[1] + 5), label, fill=(255, 0, 0))

    for point in body:
        x, y, label = point
        point = (x * 512, y * 512)
        draw.ellipse((point[0] - 3, point[1] - 3, point[0] + 3, point[1] + 3), fill=(255, 0, 0))
        draw_text.ellipse((point[0] - 3, point[1] - 3, point[0] + 3, point[1] + 3), fill=(255, 0, 0))
        draw_text.text((point[0] + 5, point[1] + 5), label, fill=(255, 0, 0))

    # show the image
    # img.show()
    plt.subplot(1, 3, 2)
    plt.imshow(img)
    plt.subplot(1, 3, 3)
    plt.imshow(img_copy)
    plt.show()


if __name__ == "__main__":
    # get all xml file path in the given folder
    xml_dir = "data"
    xml_paths = glob.glob(os.path.join(xml_dir, "*.xml"))
    if len(xml_paths) == 0:
        print("No xml file in the given folder!")
        sys.exit(0)
    pose = get_pose_from_xml(xml_paths[-1])
