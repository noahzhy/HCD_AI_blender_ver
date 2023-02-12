import os
import sys
import time
import random

import bpy
import bpy_extras
import numpy as np
# from PIL import Image
from mathutils import Vector


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

# function to generate file name with timestamp and a random 8 digit number
# timestamp format: %Y%m%d_%H%M%S
# return: baseFileName_timestamp_random8digit if baseFileName is not None
#         timestamp_random8digit if baseFileName is None
def generate_file_name(baseFileName=None):
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    random8digit = random.randint(10000000, 99999999)
    if baseFileName is None: return timestamp + '_' + str(random8digit)
    return baseFileName + '_' + timestamp + '_' + str(random8digit)


# function to make object look at the given point
def look_at(obj_name, point=Vector((0, 0, 0))):
    obj = bpy.data.objects[obj_name]
    loc = obj.location
    rot = obj.rotation_euler
    direction = point - loc
    rot = direction.to_track_quat('-Z', 'Y')
    obj.rotation_euler = rot.to_euler()


# function to set camera position and rotation randomly
def set_camera(scope=1.25, camera=None, offset_scope=0.0):
    if camera is None: camera = bpy.context.scene.camera
    # set camera position
    camera.location = Vector((random.uniform(2, 2.5), random.uniform(-scope, scope), random.uniform(-scope, scope)))
    # random point to look at
    point = Vector((
        random.uniform(-offset_scope, offset_scope),
        random.uniform(-offset_scope, offset_scope),
        random.uniform(-offset_scope, offset_scope)
    ))
    # set camera rotation
    look_at('Camera', point)
    # enable camera depth of field and set distance
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = random.uniform(1.0, 4.0)
    # random f-stop
    camera.data.dof.aperture_fstop = random.uniform(3.0, 10.0)


def random_light(light_list=[]):
    # list all lights in scene
    if len(light_list) == 0:
        for i in list_objects():
            if i.startswith('Light'):
                light_list.append(bpy.data.objects[i])

    # random light power and color
    for light in light_list:
        light.data.energy = random.uniform(10, 100)
        light.data.color = (random.uniform(0.5, 1.5), random.uniform(0.5, 1.5), random.uniform(0.5, 1.5))
        # radius
        light.data.shadow_soft_size = random.uniform(0.05, 0.5)
        # spot size
        light.data.spot_size = random.uniform(0.5, 1.5)


# border_data = [xmin, ymin, xmax, ymax]
def fast_render(file_prefix, image_dir='./', width=512, height=512, border_data=None):
    scene=bpy.context.scene
    # checks whether your output is jpeg or png
    file_format = scene.render.image_settings.file_format.lower()
    filename = f'{file_prefix}.{file_format}'
    # set output resolution
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    if border_data is not None:
        # set render border
        scene.render.use_border = True
        scene.render.border_min_x = float(border_data[0])
        scene.render.border_max_x = float(border_data[2])
        # flip y axis
        scene.render.border_min_y = round(1 - border_data[3], ndigits=6)
        scene.render.border_max_y = round(1 - border_data[1], ndigits=6)

    # write image out
    bpy.context.scene.render.filepath = f'{image_dir}/{filename}'
    bpy.ops.render.render(write_still=True)
    # return border size
    return [scene.render.border_max_x - scene.render.border_min_x, scene.render.border_max_y - scene.render.border_min_y]


# function to convert world space coordinates to camera space coordinates 2d
# normalized return value is in range [0, 1] if clamp is True
def to_camera_space_2d(vector, camera=None, clamp=True):
    if camera is None:
        camera = bpy.context.scene.camera

    scene = bpy.context.scene
    co = bpy_extras.object_utils.world_to_camera_view(scene, camera, vector)
    if clamp:
        # clamp to [0, 1]
        co.x = max(0, min(1, co.x))
        co.y = max(0, min(1, co.y))
    # keep 6 decimal places
    return (round(co.x, 6), round(co.y, 6))


# function to get object bounding box
def get_bounding_box_3d(obj_name, camera=None):
    if camera is None: camera = bpy.context.scene.camera
    # get object bounding box
    obj = bpy.data.objects[obj_name]
    # get bounding box
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    # convert to camera space
    _bbox = [to_camera_space_2d(vector, camera) for vector in bbox]
    # convert Vector to numpy array
    _bbox = np.array([np.array(vector) for vector in _bbox])
    # flip y axis
    _bbox[:, 1] = 1 - _bbox[:, 1]
    # keep four digits after decimal point
    _bbox = np.around(_bbox, decimals=6)
    return _bbox


# function to get object bounding box in camera space
# normalized return value is in range [0, 1] if clamp is True
def get_bounding_box_2d(obj_name, camera=None, is_clamp=True):
    if camera is None: camera = bpy.context.scene.camera
    #Get the inverse transformation matrix
    matrix = camera.matrix_world.normalized().inverted()
    #Create a new mesh data block, using the inverse transform matrix to undo any transformations
    dg = bpy.context.evaluated_depsgraph_get()
    mesh_object = bpy.data.objects[obj_name]
    ob = mesh_object.evaluated_get(dg) #this gives us the evaluated version of the object
    mesh = ob.to_mesh()
    #mesh = mesh_object.to_mesh()
    mesh.transform(mesh_object.matrix_world)
    mesh.transform(matrix)
    #Get the world coordinates for the camera frame bounding box, before any transformations
    scene = bpy.context.scene
    frame = [-v for v in camera.data.view_frame(scene=scene)[:3]]
    lx = []
    ly = []
    for v in mesh.vertices:
        co_local = v.co
        z = -co_local.z

        if z <= 0.0:
            #Vertex is behind the camera; ignore it
            continue
        else:
            #Perspective division
            frame = [(v / (v.z / z)) for v in frame]
        min_x, max_x = frame[1].x, frame[2].x
        min_y, max_y = frame[0].y, frame[1].y
        
        x = (co_local.x - min_x) / (max_x - min_x)
        y = (co_local.y - min_y) / (max_y - min_y)
        lx.append(x)
        ly.append(y)

    mesh_object.to_mesh_clear()
    # Image is not in view if all the mesh verts were ignored
    if not lx or not ly:
        return None

    min_x = min(lx)
    max_x = max(lx)
    min_y = min(ly)
    max_y = max(ly)

    if is_clamp:
        # clamp to [0, 1]
        min_x = max(0, min(1, min_x))
        max_x = max(0, min(1, max_x))
        min_y = max(0, min(1, min_y))
        max_y = max(0, min(1, max_y))

    # swap min and max if necessary
    if min_x > max_x: min_x, max_x = max_x, min_x
    if min_y > max_y: min_y, max_y = max_y, min_y
    # Image is not in view if both bounding points exist on the same side
    if min_x == max_x or min_y == max_y:
        return None
    # flip y axis and keep 6 decimal places
    return [round(min_x, 6), round(1 - max_y, 6), round(max_x, 6), round(1 - min_y, 6)]


# function to load fbxs with manual foward axis, Z up, Y forward
def load_animation(filepath):
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


# function to load all animations in a directory
def load_animations(dir_path):
    # delete all animations
    for anim in bpy.data.actions:
        bpy.data.actions.remove(anim)
    anims = []
    for file in os.listdir(dir_path):
        if file.endswith(".fbx"):
            anims.append(load_animation(os.path.join(dir_path, file)))
    return anims


# function to apply animation to object's bones
def apply_animation(anim_name, obj_name):
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


# function to set animation frame to every visible armature's action
def set_frame_all(frame_num=None):
    for obj in list_armatures(visible_only=True):
        set_frame(obj.animation_data.action.name, obj.name, frame_num)


# function to list objects in scene
def list_objects():
    return bpy.data.objects.keys()


# function to list all animations in the scene
def list_animations():
    anim_list = []
    for anim in bpy.data.actions:
        anim_list.append(anim.name)
    return anim_list


def list_armatures(visible_only=True):
    if visible_only:
        return [obj for obj in bpy.data.objects if obj.type == 'ARMATURE' and obj.visible_get()]
    return [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']


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
def get_hand_to_dict(obj_name):
    hand_bone_dict = {}
    for bone in bpy.data.objects[obj_name].pose.bones:
        if bone.name in hand_parts:
            # get the bone position (world space)
            hand_bone_dict[bone.name] = to_camera_space_2d(bone.matrix.to_translation())
    return hand_bone_dict


# function to list pose bones
def get_pose_to_dict(obj_name):
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


# function to hide all armature objects in the scene including its mesh
def hide_armature():
    # hide all armature objects
    for obj in list_armatures(visible_only=False):
        bpy.data.objects[obj.name].hide_viewport = True
        bpy.data.objects[obj.name].hide_render = True
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
    arma_list = list_armatures(False)
    random_armature = random.sample(arma_list, num)

    for arms in random_armature:
        bpy.data.objects[arms.name].hide_viewport = False
        bpy.data.objects[arms.name].hide_render = False
        # show its mesh
        for child in bpy.data.objects[arms.name].children:
            child.hide_viewport = False
            child.hide_render = False

    return random_armature


# function to random animation to all armature objects in the scene
def random_animation():
    for obj in list_armatures(False):
        # get all animations
        anims = list_animations()
        # random animation
        anim = random.choice(anims)
        # apply animation to object
        apply_animation(anim, obj.name)


def get_obj_from_armature(armature):
    return [obj for obj in bpy.data.objects if obj.parent == armature and obj.visible_get()]

