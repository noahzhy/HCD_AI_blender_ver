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
        # clean all action
        for arma in list_armatures(True):
            arma.animation_data_clear()

        self.persons = []
        self.file_name = generate_file_name()
        # set name of output file
        self.nodes["File Output"].file_slots[0].path = "img_{}".format(self.file_name)
        self.nodes["File Output"].file_slots[1].path = "mask_{}".format(self.file_name)
        self.nodes["File Output"].file_slots[2].path = "depth_{}".format(self.file_name)
        self.nodes["File Output"].file_slots[3].path = "body_{}".format(self.file_name)

    def render(self):
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
        # close depth of field
        bpy.context.scene.camera.data.dof.use_dof = False
        bpy.context.scene.render.film_transparent = True
        bpy.ops.render.render(write_still=True, layer=part_viewlayer)
        # render color image
        for obj in armas:
            for child in bpy.data.objects[obj.name].children:
                if child.type == "MESH":
                    bpy.context.view_layer.objects.active = child
                    bpy.context.object.modifiers["GeometryNodes"]["Input_2"] = 0
        # open depth of field
        bpy.context.scene.camera.data.dof.use_dof = True
        bpy.context.scene.render.film_transparent = False
        bpy.ops.render.render(write_still=True, layer=main_viewlayer)

    def gen_xml(self):
        arma_list = list_armatures(visible_only=True)
        for idx, arma in enumerate(arma_list):
            # get mesh object
            mesh_obj = get_obj_from_armature(arma)[0]
            bbox = get_bounding_box_2d(mesh_obj.name, is_clamp=True)
            if bbox is None: continue
            # get keypoint
            pose = get_pose_to_dict(arma.name)
            hand = get_hand_to_dict(arma.name)
            person = Person(bbox, pose, hand)
            self.persons.append(person)

        # get render x y
        render_x = bpy.context.scene.render.resolution_x
        render_y = bpy.context.scene.render.resolution_y
        # get render img format channel
        render_format = bpy.context.scene.render.image_settings.file_format
        # get render img channel
        render_c = 3 if render_format == "RGB" else 4
        # get output file name
        save_xml(
            self.persons,
            "img_{}{:04d}.png".format(self.file_name, bpy.context.scene.frame_current),
            self.outpath,
            render_x, render_y, render_c
        )

    def gen_data(self):
        self.reset()
        show_armature(1)
        random_animation()
        set_frame_all(-1)
        random_armature_position()

        # update camera
        v3 = get_bone_pos('nose')
        print("LeftHand pos: ", v3)
        random_light(target_origin=v3, scope=1.0)
        random_camera(dst_point=v3, offset_scope=0.1)

        # self.render()
        # self.gen_xml()


if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(bpy.data.filepath), "data")
    ss = SynthData(1, debug=False, outpath=output_path)
    ss.gen_data()
