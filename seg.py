import os
import sys
import random

import bpy

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import importlib
import anim
import base_ops
import skeleton2xml
importlib.reload(anim)
importlib.reload(base_ops)
importlib.reload(skeleton2xml)
from anim import *
from base_ops import *
from skeleton2xml import *


class SynthSeg():
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
        pass

    def render(self):
        for i in range(self.num):
            # random flip axis
            self.nodes["flip"].axis = random.choice(["X", "Y", "XY"])
            # random angle in degrees [0, 90, 180, 270]
            angle = random.randint(0, 3) * 90
            # set rotation angle
            self.nodes["angle of rotation"].outputs[0].default_value = float(angle)
            # # render and save
            if not self.debug:
                self.render_layers()

            print("rendering folder path: ", os.path.join(self.outpath))

    def render_layers(self, main_viewlayer='ViewLayer', part_viewlayer='ViewLayer_part'):
        armas = self.list_armature()
        # choose armature object mesh
        for obj in armas:
            # if is mesh
            for child in bpy.data.objects[obj].children:
                if child.type == "MESH": bpy.context.object.modifiers["GeometryNodes"]["Input_2"] = 1
        bpy.ops.render.render(write_still=True, layer=part_viewlayer)
        # render color image
        for obj in armas:
            for child in bpy.data.objects[obj].children:
                if child.type == "MESH": bpy.context.object.modifiers["GeometryNodes"]["Input_2"] = 0
        bpy.ops.render.render(write_still=True, layer=main_viewlayer)

    def gen_xml(self):
        persons = []

        arma_list = list_all_visible_armas()
        for idx, arma in enumerate(arma_list):
            # get mesh object
            mesh_obj = get_obj_from_armature(arma)[0]
            bbox = get_bounding_box_2d(mesh_obj.name)
            pose = pose_bones_to_dict(arma.name)
            hand = hand_bones_to_dict(arma.name)
            person = Person(bbox, pose, hand)
            persons.append(person)

        save_xml(
            persons,
            "E:\\projects\\HCD_AI_blender_ver\\data\\img_0009.png",
            "E:\\projects\\HCD_AI_blender_ver\\data",
            512, 512, 3
        )

    # @staticmethod
    # def list_armature():
    #     return [obj.name for obj in bpy.data.objects if obj.type == "ARMATURE" and obj.visible_get()]

    # @staticmethod
    # def get_bones(armature):
    #     bones = []
    #     for bone in armature.data.bones:
    #         bones.append(bone.name)
    #     return bones


if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(bpy.data.filepath), "data")
    ss = SynthSeg(1, debug=False, outpath=output_path)
    arma_list = list_all_visible_armas()

    ss.gen_xml()

    # for arma in arma_list:
    #     bones = ss.get_bones(bpy.data.objects[arma.name])
    #     print(bones)

    # ss.render()
