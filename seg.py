import os
import sys
import random

import bpy

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import importlib
import base_ops
import xml_tools
importlib.reload(base_ops)
importlib.reload(xml_tools)
from base_ops import *
from xml_tools import *


class SynthData():
    def __init__(self, num, debug=False, outpath=""):
        self.num = num
        self.debug = debug
        self.outpath = outpath
        # init scene
        scene = bpy.context.scene
        scene.use_nodes = True
        self.nodes = scene.node_tree.nodes
        self.nodes["File Output"].base_path = outpath
        self.reset()

    def reset(self):
        self.persons = []
        self.file_name = generate_file_name()
        # set name of output file
        self.nodes["File Output"].file_slots[0].path = "img_{}".format(self.file_name)
        self.nodes["File Output"].file_slots[1].path = "mask_{}".format(self.file_name)
        self.nodes["File Output"].file_slots[2].path = "depth_{}".format(self.file_name)
        self.nodes["File Output"].file_slots[3].path = "body_{}".format(self.file_name)

    def render(self):
        # random flip axis
        self.nodes["flip"].axis = random.choice(["X", "Y", "XY"])
        # random angle in degrees [0, 90, 180, 270]
        angle = random.randint(0, 3) * 90
        # set rotation angle
        self.nodes["angle of rotation"].outputs[0].default_value = float(angle)
        # render and save
        if not self.debug: self.render_layers()

        # set name of output file

        print("rendering folder path: ", os.path.join(self.outpath))

    def render_layers(self, main_viewlayer='ViewLayer', part_viewlayer='ViewLayer_part'):
        armas = list_armatures(visible_only=True)
        # choose armature object mesh
        for obj in armas:
            # if is mesh
            for child in bpy.data.objects[obj.name].children:
                if child.type == "MESH":
                    # select mesh object
                    bpy.context.view_layer.objects.active = child
                    bpy.context.object.modifiers["GeometryNodes"]["Input_2"] = 1
        bpy.ops.render.render(write_still=True, layer=part_viewlayer)
        # render color image
        for obj in armas:
            for child in bpy.data.objects[obj.name].children:
                if child.type == "MESH":
                    bpy.context.view_layer.objects.active = child
                    bpy.context.object.modifiers["GeometryNodes"]["Input_2"] = 0
        bpy.ops.render.render(write_still=True, layer=main_viewlayer)

    def gen_data(self):
        self.reset()
        show_armature(1)
        random_animation()
        set_frame_all(-1)
        self.render()
        self.gen_xml()

    def gen_xml(self):
        arma_list = list_armatures(visible_only=True)
        for idx, arma in enumerate(arma_list):
            # get mesh object
            mesh_obj = get_obj_from_armature(arma)[0]
            bbox = get_bounding_box_2d(mesh_obj.name, is_clamp=True)
            pose = get_pose_to_dict(arma.name)
            hand = get_hand_to_dict(arma.name)
            person = Person(bbox, pose, hand)
            self.persons.append(person)

        # get output file name
        save_xml(
            self.persons,
            "img_{}{:04d}.png".format(self.file_name, bpy.context.scene.frame_current),
            self.outpath,
            512, 512, 4
        )


if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(bpy.data.filepath), "data")
    ss = SynthData(1, debug=False, outpath=output_path)
    ss.gen_data()
