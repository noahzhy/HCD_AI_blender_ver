import os
import sys
import random
from mathutils import Vector

import bpy
import bpy_extras

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import base_ops
import importlib
importlib.reload(base_ops)
from base_ops import *

# pose part names
pose_parts = {
    'nose': 'Nose',
    'Neck': 'Neck',
    'RightArm': 'RightArm', 'RightForeArm': 'RightForeArm', 'RightHand': 'RightHand',
    'LeftArm': 'LeftArm', 'LeftForeArm': 'LeftForeArm', 'LeftHand': 'LeftHand',
    'RightUpLeg': 'RightUpLeg', 'RightLeg': 'RightLeg', 'RightFoot': 'RightFoot',
    'LeftUpLeg': 'LeftUpLeg', 'LeftLeg': 'LeftLeg', 'LeftFoot': 'LeftFoot',
    'RightEye': 'RightEye', 'LeftEye': 'LeftEye',
    'ear_r': 'RightEar', 'ear_l': 'LeftEar',
}

# hands part names
hand_parts = [
    'LeftHand',
    'LeftHandThumb1', 'LeftHandThumb2', 'LeftHandThumb3', 'LeftHandThumb4',
    'LeftHandIndex1', 'LeftHandIndex2', 'LeftHandIndex3', 'LeftHandIndex4',
    'LeftHandMiddle1', 'LeftHandMiddle2', 'LeftHandMiddle3', 'LeftHandMiddle4',
    'LeftHandRing1', 'LeftHandRing2', 'LeftHandRing3', 'LeftHandRing4',
    'LeftHandPinky1', 'LeftHandPinky2', 'LeftHandPinky3', 'LeftHandPinky4',
    'RightHand', 
    'RightHandThumb1', 'RightHandThumb2', 'RightHandThumb3', 'RightHandThumb4',
    'RightHandIndex1', 'RightHandIndex2', 'RightHandIndex3', 'RightHandIndex4',
    'RightHandMiddle1', 'RightHandMiddle2', 'RightHandMiddle3', 'RightHandMiddle4',
    'RightHandRing1', 'RightHandRing2', 'RightHandRing3', 'RightHandRing4',
    'RightHandPinky1', 'RightHandPinky2', 'RightHandPinky3', 'RightHandPinky4',
]

# function to load fbxs with manual foward axis, Z up, Y forward
def load_anim(filepath):
    # manual orientation, Y forward, Z up
    bpy.ops.import_scene.fbx(
        filepath=filepath,
        axis_forward='Y',
        axis_up='Z',
        use_manual_orientation=True,
        use_custom_normals=True,
        use_image_search=False,
        use_alpha_decals=False,
        decal_offset=0.0,
        use_anim=True,
        anim_offset=1.0,
        bake_space_transform = False,
        use_prepost_rot = False,
        use_custom_props=True,
        use_custom_props_enum_as_string=True,
        ignore_leaf_bones=True,
        force_connect_children=False,
        automatic_bone_orientation=False,
    )
    # rename the fbx to the file name
    fbx_name = filepath.split("\\")[-1].split(".")[0]
    # delete same name animation if exists
    if fbx_name in bpy.data.actions:
        bpy.data.actions.remove(bpy.data.actions[fbx_name])
    # rename their animation to the file name
    bpy.context.selected_objects[0].animation_data.action.name = fbx_name
    # delete the object and keep animation
    bpy.ops.object.delete(use_global=False, confirm=False)
    # return animation name
    return fbx_name


def load_anims(dir_path):
    # delete all animations
    for anim in bpy.data.actions:
        bpy.data.actions.remove(anim)
    anims = []
    for file in os.listdir(dir_path):
        if file.endswith(".fbx"):
            anims.append(load_anim(os.path.join(dir_path, file)))
    return anims


# function to apply animation to object's bones
def apply_anim(anim_name, obj_name):
    # if the object has no animation, create an empty animation
    if bpy.data.objects[obj_name].animation_data is None:
        bpy.data.objects[obj_name].animation_data_create()
    # select the object
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[obj_name].select_set(True)
    # select the animation
    bpy.data.objects[obj_name].animation_data.action = bpy.data.actions[anim_name]
    # apply animation to object
    bpy.ops.nla.bake(frame_start=0, frame_end=0, only_selected=False, visual_keying=True, clear_constraints=False, use_current_action=True, bake_types={'POSE'})


# function to frame the animation via given frame number
def set_frame(anim_name, obj_name, frame_num=None):
    action = bpy.data.actions[anim_name]
    # select the animation
    bpy.data.objects[obj_name].animation_data.action = action
    # if frame number is not given, randomize it
    if frame_num is None or frame_num == -1:
        frame_num = random.randint(action.frame_range[0], action.frame_range[1])
    # check if frame number is in range
    if frame_num > action.frame_range[1]:
        frame_num = action.frame_range[1]
    if frame_num < action.frame_range[0]:
        frame_num = action.frame_range[0]
    # set the frame
    bpy.context.scene.frame_set(frame_num)
    return frame_num


# function to list all animations in the scene
def list_anim():
    anim_list = []
    for anim in bpy.data.actions:
        anim_list.append(anim.name)
    return anim_list


# function to list all bones in the scene via given object name
def list_bones(obj_name):
    bone_list = []
    for bone in bpy.data.objects[obj_name].pose.bones:
        bone_list.append(bone.name)
    return bone_list


# function to list bones position in the scene via given object name, bone name
def list_bone_pos(obj_name, bone_name):
    bone_pos = []
    for bone in bpy.data.objects[obj_name].pose.bones:
        if bone.name == bone_name:
            bone_pos.append(bone.location)
    return bone_pos


# function to list hands bones
def hand_bones_to_dict(obj_name):
    hand_bone_dict = {}
    for bone in bpy.data.objects[obj_name].pose.bones:
        if bone.name in hand_parts:
            # get the bone position (world space)
            hand_bone_dict[bone.name] = to_camera_space_2d(bone.matrix.to_translation())
    return hand_bone_dict


# function to list pose bones
def pose_bones_to_dict(obj_name):
    pose_bone_dict = {}
    for bone in bpy.data.objects[obj_name].pose.bones:
        if bone.name in pose_parts.keys():
            pose_bone_dict[pose_parts[bone.name]] = to_camera_space_2d(bone.matrix.to_translation())
    return pose_bone_dict


# function to list all .fbx file names via given directory and file extension
def load_files(directory, extension):
    file_list = []
    for file in os.listdir(directory):
        if file.endswith(extension):
            file_list.append(file)
    return file_list


# function to list all armature objects in the scene
def list_armature(scene_name=None):
    # list all scene names if scene name is not given
    if scene_name is None:
        scene_name = bpy.data.scenes[0].name

    obj_list = []
    for obj in bpy.data.scenes[scene_name].objects:
        if obj.type == "ARMATURE":
            obj_list.append(obj.name)
    return obj_list


# function to convert world space coordinates to camera space coordinates 2d
# normalized return value is in range [0, 1]
def to_camera_space_2d(vector, camera=None):
    if camera is None:
        camera = bpy.context.scene.camera
    scene = bpy.context.scene
    co = bpy_extras.object_utils.world_to_camera_view(scene, camera, vector)
    # flip y
    co.y = 1 - co.y
    # return (co.x, co.y)
    # keep 6 decimal places
    return (round(co.x, 6), round(co.y, 6))


# function to hide all armature objects in the scene including its mesh
def hide_armature():
    # list all armature objects
    arma_list = list_armature()
    # hide all armature objects
    for obj in arma_list:
        bpy.data.objects[obj].hide_viewport = True
        bpy.data.objects[obj].hide_render = True
    # hide all armature objects' mesh
    for obj in bpy.data.objects:
        if obj.parent is not None and obj.parent.type == "ARMATURE":
            obj.hide_viewport = True
            obj.hide_render = True


# function to hide all armature objects in the scene, but random pick one to show and show its mesh
def show_armature(num=None):
    random_armature = []
    # hide all armature objects
    hide_armature()

    # list all armature objects
    if num is None: num = 1
    arma_list = list_armature()
    random_armature = random.sample(arma_list, num)

    for arms in random_armature:
        bpy.data.objects[arms].hide_viewport = False
        bpy.data.objects[arms].hide_render = False
        # show its mesh
        for child in bpy.data.objects[arms].children:
            child.hide_viewport = False
            child.hide_render = False

    return random_armature


if __name__ == "__main__":
    # get the file path
    f_path = os.path.join(os.path.dirname(bpy.data.filepath), "anim")

    anims = load_anims(f_path)
    armas = show_armature()
    print(anims)

    arms_visible = list_all_visible_armas()
    print(arms_visible)

    # for arma in armas:
    #     anim_name = random.choice(anims)
    #     apply_anim(anim_name, arma)
    #     set_frame(anim_name, arma, -1)

    # for obj in arma:
    #     anim_name = random.choice(anims)
    #     apply_anim(anim_name, obj)
    #     set_frame(anim_name, obj, -1)

    pose = pose_bones_to_dict(armas[0])

    # print(list_anim())
    # print(hand_bones_to_dict("carla"))
    # pose = pose_bones_to_dict("carla")
    # using vector_to_2d function to convert 3d Vector to 2d
    for key, value in pose.items():
        print(key, to_camera_space_2d(value))
