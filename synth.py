import os
import sys
import random
import datetime

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
    def __init__(self, num, debug=False, outpath="", hdr_path="", env_light=True):
        self.num = num
        self.debug = debug
        self.outpath = outpath
        self.hdr_path = hdr_path
        self.env_light = env_light
        # init scene
        scene = bpy.context.scene
        scene.use_nodes = True
        self.nodes = scene.node_tree.nodes
        self.nodes["Image Output"].base_path = outpath
        self.nodes["File Output"].base_path = outpath
        # load env map
        load_hdrs(self.hdr_path)
        # reset the export node value
        self.reset()

    def reset(self):
        # random select a hdr
        random_hdr()
        # clean all action
        for arma in list_armatures(True):
            arma.animation_data_clear()

        self.persons = []
        self.file_name = generate_file_name()
        # set name of output file
        self.nodes["Image Output"].file_slots[0].path = "img_{}".format(self.file_name)
        self.nodes["File Output"].file_slots[0].path = "body_{}".format(self.file_name)
        self.nodes["File Output"].file_slots[1].path = "mask_{}".format(self.file_name)
        self.nodes["File Output"].file_slots[2].path = "depth_{}".format(self.file_name)

    def render(self):
        # render and save
        if not self.debug:
            self.render_layers()
            self.gen_xml()
        # set name of output file
        print("rendering folder path: ", os.path.join(self.outpath))

    def render_layers(self, main_viewlayer='ViewLayer', part_viewlayer='ViewLayer_part'):
        armas = list_armatures(visible_only=True)
        # render mask image
        # choose armature object mesh
        for obj in armas:
            # if is mesh
            for child in bpy.data.objects[obj.name].children:
                if child.type == "MESH":
                    # select mesh object
                    bpy.context.view_layer.objects.active = child
                    bpy.context.object.modifiers["GeometryNodes"]["Input_2"] = 1

        easy_mask_mode()
        single_render(part_viewlayer)

        # render color image
        for obj in armas:
            for child in bpy.data.objects[obj.name].children:
                if child.type == "MESH":
                    bpy.context.view_layer.objects.active = child
                    bpy.context.object.modifiers["GeometryNodes"]["Input_2"] = 0

        # open depth of field
        bpy.context.scene.camera.data.dof.use_dof = True
        bpy.context.scene.render.film_transparent = False
        # open motion blur
        bpy.context.scene.render.use_motion_blur = True
        # open render noise
        bpy.context.scene.cycles.samples = 256
        # open denoise
        bpy.context.scene.cycles.use_denoising = True
        # bake settings to ADJACENT_FACES
        bpy.context.scene.render.bake.margin_type = 'ADJACENT_FACES'
        single_render(main_viewlayer)

    def gen_xml(self):
        arma_list = list_armatures(visible_only=True)
        for idx, arma in enumerate(arma_list):
            # get mesh object
            mesh_obj = get_obj_from_armature(arma)[0]
            bbox = get_bounding_box_2d(mesh_obj.name)
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
        # show_armature(1)
        random_animation()
        set_frame_all(-1)
        random_armature_position()

        # update camera
        armature = list_armatures(visible_only=True)[0]
#        v3 = get_bone_pos_global(armature, 'nose')
        v3 = get_bone_pos_global(armature, 'RightHand')
        random_camera(dst_point=v3, offset_scope=0.1, pos_scale=1.5)

        if self.env_light:
            random_light(target_origin=v3, scope=1.0)

        self.render()


if __name__ == "__main__":
    base_dir = os.path.dirname(bpy.data.filepath)
    output_path = os.path.join(base_dir, "data")
    hdr_path = os.path.join(base_dir, "hdrs")
    ss = SynthData(1, debug=False, outpath=output_path, hdr_path=hdr_path)
    current_time = datetime.datetime.now()
    ss.gen_data()
    use_time = (datetime.datetime.now() - current_time).microseconds
    # to second
    use_time = use_time / 1000000
    print("use time: ", use_time)
