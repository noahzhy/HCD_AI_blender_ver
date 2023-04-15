import os
import sys
import time
import glob
import math
import random

import bpy
import bpy_extras
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


pose_head = ['nose', 'ear_r', 'ear_l', 'eye_end_r', 'eye_end_l',]

# pose part names
pose_parts = {
    'nose': 'Nose',
    'Neck': 'Neck',
    'RightArm': 'RightArm', 'RightForeArm': 'RightForeArm', 'RightHand': 'RightHand',
    'LeftArm': 'LeftArm', 'LeftForeArm': 'LeftForeArm', 'LeftHand': 'LeftHand',
    'RightUpLeg': 'RightUpLeg', 'RightLeg': 'RightLeg', 'RightFoot': 'RightFoot',
    'LeftUpLeg': 'LeftUpLeg', 'LeftLeg': 'LeftLeg', 'LeftFoot': 'LeftFoot',
    'eye_end_r': 'RightEye', 'eye_end_l': 'LeftEye',
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
def look_at(obj_name=None, point=Vector((0, 0, 0))):
    if obj_name is None:
        obj = bpy.context.scene.camera
    else:
        obj = bpy.data.objects[obj_name]
    loc = obj.location
    rot = obj.rotation_euler
    direction = point - loc
    rot = direction.to_track_quat('-Z', 'Y')
    obj.rotation_euler = rot.to_euler()


def random_camera(camera=None, dst_point=Vector((0,0,0)), pos_scale=.5, offset_scope=0.0):
    x, y, z = dst_point
    if camera is None: camera = bpy.context.scene.camera
    # set camera position
    camera.location = Vector((
        random.uniform(x-pos_scale, x+pos_scale),
        random.uniform(y-0.75*pos_scale, y-1.5*pos_scale),
        random.uniform(z-pos_scale, z+pos_scale)
    ))
    # random point to look at
    point = Vector((
        random.uniform(x - offset_scope, x + offset_scope),
        # random.uniform(y - offset_scope, y + offset_scope),
        y,
        random.uniform(z - offset_scope, z + offset_scope)
    ))
    # set camera rotation
    look_at('Camera', point)
    # enable camera depth of field and set distance
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = pos_scale


def random_light(light_list=[], target_origin=Vector((0,0,0)), scope=0.0, power_scope=[250, 750]):
    # list all lights in scene
    if len(light_list) == 0:
        for i in list_objects():
            if i.startswith('Light'):
                light_list.append(bpy.data.objects[i])

    # random light power and color
    for light in light_list:
        # random light postion
        light.location = Vector((
            random.uniform(target_origin[0] - scope, target_origin[0] + scope),
            random.uniform(target_origin[1] - scope, target_origin[1] + scope),
            random.uniform(target_origin[2] - scope, target_origin[2] + scope)
        ))
        light.data.energy = random.uniform(power_scope[0], power_scope[1])
        light.data.color = (random.uniform(0.5, 1.5), random.uniform(0.5, 1.5), random.uniform(0.5, 1.5))
        # radius
        light.data.shadow_soft_size = random.uniform(1.0, 2.5)


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

    co = world_to_camera_view(bpy.context.scene, camera, vector)
    # flip y axis
    co.y = 1 - co.y
    if clamp:
        # clamp to [0, 1]
        co.x = max(0, min(1, co.x))
        co.y = max(0, min(1, co.y))
    # keep 6 decimal places
    return (round(co.x, 6), round(co.y, 6))


# function to get object bounding box in camera space
# normalized return value is in range [0, 1] if clamp is True
def get_bounding_box_2d(obj_name, camera=None):
    if camera is None: camera = bpy.context.scene.camera
    # Get the inverse transformation matrix
    matrix = camera.matrix_world.normalized().inverted()
    # Create a new mesh data block, using the inverse transform matrix to undo any transformations
    dg = bpy.context.evaluated_depsgraph_get()
    mesh_object = bpy.data.objects[obj_name]
    mesh = mesh_object.evaluated_get(dg).to_mesh()
    mesh.transform(mesh_object.matrix_world)
    mesh.transform(matrix)
    # Get the world coordinates for the camera frame bounding box, before any transformations
    scene = bpy.context.scene
    frame = [-v for v in camera.data.view_frame(scene=scene)[:3]]

    # Calculate bounding box coordinates
    lx, ly = [], []
    for v in mesh.vertices:
        co_local = v.co
        z = -co_local.z

        if z >= 0.0:
            # Perspective division
            frame = [(v / (v.z / z)) for v in frame]

            min_x, max_x = frame[1].x, frame[2].x
            min_y, max_y = frame[0].y, frame[1].y

            x = (co_local.x - min_x) / (max_x - min_x)
            y = (co_local.y - min_y) / (max_y - min_y)

            if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
                lx.append(x)
                # flip y axis
                ly.append(1 - y)

    # Free the memory used by the mesh
    mesh_object.to_mesh_clear()

    # Return None if the mesh is not in view
    if not lx or not ly: return None

    # Calculate bounding box coordinates
    min_x, max_x = min(lx), max(lx)
    min_y, max_y = min(ly), max(ly)

    # return the result
    return [round(min_x, 6), round(min_y, 6), round(max_x, 6), round(max_y, 6)]


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


# function to random animation to all armature objects in the scene
def random_animation():
    for obj in list_armatures(True):
        # get all animations
        anims = list_animations()
        # random animation
        anim = random.choice(anims)
        # apply animation to object
        apply_animation(anim, obj.name)


# function to set random armature position via given armature name
def random_armature_position(scope=2.5, rotate_scope=30, scale_scope=.5):
    for obj in list_armatures(True):
        # randomize position
        obj.location = (random.uniform(-scope, scope), random.uniform(-scope, scope), obj.location.z)
        # obj.rotation_euler = (0, 0, random.uniform(-rotate_scope, rotate_scope))
        # _scale = random.uniform(1 - scale_scope, 1 + scale_scope)
        # obj.scale = (_scale, _scale, _scale)
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)


# function to frame the animation via given frame number
def set_frame(anim_name, obj_name, frame_num=None):
    action = bpy.data.actions[anim_name]
    # select the animation
    bpy.data.objects[obj_name].animation_data.action = action
    # if frame number is not given, randomize it
    if frame_num is None or frame_num == -1:
        frame_num = random.randint(action.frame_range[0]+2, action.frame_range[1])
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


# function to get bone position via given armature name, bone name
def get_bone_pos(bone_name):
    target_bone_pos = Vector((0, 0, 0))
    for armas in list_armatures(visible_only=True):
        bpy.data.objects[armas.name].select_set(True)
        for bone in armas.pose.bones:
            # get global position in 3d space
            if bone.name == bone_name:
                mv = armas.convert_space(pose_bone=bone, matrix=bone.matrix, from_space='POSE', to_space='WORLD')
                mv = mv.to_translation()
                # add the position of the armature
                mv += armas.location
                target_bone_pos = mv

    return target_bone_pos


# function to list hands bones
def get_hand_to_dict(obj_name, camera=None):
    if camera is None:
        camera = bpy.data.objects['Camera']
    hand_bone_dict = {}
    aram = bpy.data.objects[obj_name]
    for bone in aram.pose.bones:
        if bone.name in hand_parts:
            # get the bone position (world space)
            x, y = to_camera_space_2d(bone.matrix.to_translation(), clamp=False)
            boneVec = get_bone_pos_global(aram, bone.name)
            occ = is_occluded(camera, boneVec)
            # convert true/false to 1/0
            occ = 1 if occ else 0
            hand_bone_dict[bone.name] = (x, y, occ)
    return hand_bone_dict


# function to list pose bones
def get_pose_to_dict(obj_name, camera=None):
    if camera is None:
        camera = bpy.data.objects['Camera']

    pose_bone_dict = {}
    aram = bpy.data.objects[obj_name]

    for bone in aram.pose.bones:
        if bone.name in pose_parts.keys():
            # get the bone position (world space)
            x, y = to_camera_space_2d(bone.matrix.to_translation(), clamp=False)
            boneVec = get_bone_pos_global(aram, bone.name)
            # if bone.name not in pose_head:
            if bone.name in pose_head:
                print(bone.name, "===============")
                occ = is_occluded(camera, boneVec, .005)
            elif bone.name in hand_parts:
                occ = is_occluded(camera, boneVec, .005)
            else:
                occ = is_occluded(camera, boneVec)
            # convert true/false to 1/0
            occ = 1 if occ else 0
            pose_bone_dict[pose_parts[bone.name]] = (x, y, occ)

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


def get_obj_from_armature(armature):
    return [obj for obj in bpy.data.objects if obj.parent == armature and obj.visible_get()]


# hdrs function
def load_hdrs(directory=None):
    # clear all images which start with 'env'
    for img in bpy.data.images:
        if img.name.startswith('env'):
            bpy.data.images.remove(img)

    if directory is None:
        os.path.join(os.path.dirname(bpy.data.filepath), "hdrs")

    # load it in blender and rename it using basename
    for hdr in glob.glob(os.path.join(directory, "*.*")):
        bpy.ops.image.open(filepath=hdr, files=[{"name":hdr}], relative_path=True, show_multiview=False)


def set_hdr(hdr_name):
    bpy.data.worlds['World'].node_tree.nodes['Environment Texture'].image = hdr_name


def random_hdr():
    # list all images which start with 'env'
    hdr_list = [img for img in bpy.data.images if img.name.startswith('env')]
    set_hdr(random.choice(hdr_list))


# only for testing
# function to get bone position in camera view using view3d_utils
def get_bone_pos_global(armature, bone_name):
    bone = armature.pose.bones[bone_name]
    return armature.matrix_world @ bone.head


def occlusion_ray(scene, dg, origin, direction, distance=1000):
    direction.normalized()
    is_hit, loc, _, index, hit_obj, _ = scene.ray_cast(
        dg,
        origin,
        direction,
        distance=distance
    )

    if is_hit:
        return is_hit, hit_obj.name_full, index
    else:
        return is_hit, None, None


def is_occluded(camera, boneVec, threshold=.2):
    scene = bpy.context.scene
    # get vectors which define view frustum of camera
    top_left = camera.data.view_frame(scene=scene)[-1]

    # convert [0, 1] to [-.5, .5]
    x, y, _ = world_to_camera_view(scene, camera, boneVec)
    pix_vec = Vector((x-.5, y-.5, top_left[2]))
    pix_vec.rotate(camera.matrix_world.to_quaternion())

    # direction_hit equal to visible check
    return not direction_hit(scene, boneVec, -pix_vec, dist=threshold)


def direction_hit(scene, loc, direction, dist=1):
    init_status = False
    dg = bpy.context.evaluated_depsgraph_get()
    e = 1e-6

    is_hit, loc, _, _, _, _ = scene.ray_cast(
        dg, loc, direction, distance=dist
    )
    # does not hit anything, be occluded by other bones
    if not is_hit: return False

    while(is_hit):
        loc += e * direction
        is_hit, loc, normal, _, _, _ = scene.ray_cast(
            dg, loc, direction
        )
        # hit normal direction is opposite to ray direction
        if normal.dot(direction) < 0: return False

    return True


def easy_mask_mode():
    """
    a simple function to set settings for mask rendering
    """
    # close depth of field
    bpy.context.scene.camera.data.dof.use_dof = False
    # transparent background
    bpy.context.scene.render.film_transparent = True
    # close motion blur
    bpy.context.scene.render.use_motion_blur = False
    # close render noise
    bpy.context.scene.cycles.samples = 1
    # close denoising
    bpy.context.scene.cycles.use_denoising = False
    # bake settings to 
    bpy.context.scene.render.bake.margin_type = 'EXTEND'


def single_render(layer_name):
    bpy.context.scene.render.use_single_layer = False
    bpy.context.scene.view_layers[layer_name].use = False
    bpy.ops.render.render()
    bpy.ops.render.render(layer=layer_name)
