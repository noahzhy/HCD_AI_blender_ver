import os
import sys
import time
import random

import bpy
import bpy_extras
import numpy as np
# from PIL import Image
from mathutils import Vector


# function to generate file name with timestamp and a random 8 digit number
# timestamp format: %Y%m%d_%H%M%S
# return: baseFileName_timestamp_random8digit
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
def set_camera(scope=1.25, camera=bpy.data.objects['Camera'], offset_scope=0.0):
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


# function to list objects in scene
def list_objects():
    return bpy.data.objects.keys()

# function to convert world space coordinates to camera space coordinates 2d
# normalized return value is in range [0, 1]
def to_camera_space_2d(vector, camera=bpy.data.objects['Camera']):
    scene = bpy.context.scene
    co = bpy_extras.object_utils.world_to_camera_view(scene, camera, vector)
    # clamp to [0, 1]
    co.x = max(0, min(1, co.x))
    co.y = max(0, min(1, co.y))
    return Vector((co.x, co.y))


# function to get object bounding box
def get_bounding_box_3d(obj_name, camera=bpy.data.objects['Camera']):
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


def get_bounding_box_2d(obj_name, camera=bpy.data.objects['Camera']):
    #Get the inverse transformation matrix
    matrix = camera.matrix_world.normalized().inverted()
    #Create a new mesh data block, using the inverse transform matrix to undo any transformations
    dg = bpy.context.evaluated_depsgraph_get()
    mesh_object = bpy.data.objects[obj_name]
    ob = mesh_object.evaluated_get(dg) #this gives us the evaluated version of the object. Aka with all modifiers and deformations applied.
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

    min_x = np.clip(min(lx), 0.0, 1.0).round(6)
    max_x = np.clip(max(lx), 0.0, 1.0).round(6)
    # # flip y axis
    min_y = (1 - np.clip(min(ly), 0.0, 1.0)).round(6)
    max_y = (1 - np.clip(max(ly), 0.0, 1.0)).round(6)
    # swap min and max if necessary
    if min_x > max_x: min_x, max_x = max_x, min_x
    if min_y > max_y: min_y, max_y = max_y, min_y
    # Image is not in view if both bounding points exist on the same side
    if min_x == max_x or min_y == max_y:
        return None

    return [min_x, min_y, max_x, max_y]


def list_all_visible_armas():
    return [obj for obj in bpy.data.objects if obj.type == 'ARMATURE' and obj.visible_get()]


def get_obj_from_armature(armature):
    return [obj for obj in bpy.data.objects if obj.parent == armature and obj.visible_get()]
