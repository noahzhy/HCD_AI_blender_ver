import os
import sys
import random

import bpy

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import base_ops
import importlib
importlib.reload(base_ops)
from base_ops import *


# pose_lookup = [
#     'nose',
#     'Neck',
#     'RightArm', 'RightForeArm', 'RightHand',
#     'LeftArm', 'LeftForeArm', 'LeftHand',
#     'RightUpLeg', 'RightLeg', 'RightFoot',
#     'LeftUpLeg', 'LeftLeg', 'LeftFoot',
#     'RightEye', 'LeftEye',
#     'ear_r', 'ear_l',
# ]

# hand_lookup = [
#     'LeftHand',
#     'LeftHandThumb1', 'LeftHandThumb2', 'LeftHandThumb3', 'LeftHandThumb4',
#     'LeftHandIndex1', 'LeftHandIndex2', 'LeftHandIndex3', 'LeftHandIndex4',
#     'LeftHandMiddle1', 'LeftHandMiddle2', 'LeftHandMiddle3', 'LeftHandMiddle4',
#     'LeftHandRing1', 'LeftHandRing2', 'LeftHandRing3', 'LeftHandRing4',
#     'LeftHandPinky1', 'LeftHandPinky2', 'LeftHandPinky3', 'LeftHandPinky4',
#     'RightHand', 
#     'RightHandThumb1', 'RightHandThumb2', 'RightHandThumb3', 'RightHandThumb4',
#     'RightHandIndex1', 'RightHandIndex2', 'RightHandIndex3', 'RightHandIndex4',
#     'RightHandMiddle1', 'RightHandMiddle2', 'RightHandMiddle3', 'RightHandMiddle4',
#     'RightHandRing1', 'RightHandRing2', 'RightHandRing3', 'RightHandRing4',
#     'RightHandPinky1', 'RightHandPinky2', 'RightHandPinky3', 'RightHandPinky4',
# ]


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

    # for arma in arma_list:
    #     bones = ss.get_bones(bpy.data.objects[arma.name])
    #     print(bones)

    # ss.render()
