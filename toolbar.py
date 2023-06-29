import os
import sys
import time
import math
import random

import bpy

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import importlib
import base_ops
importlib.reload(base_ops)
from base_ops import *

from bpy.props import *
from mathutils import Vector


pose_parts = {
    'nose',
    'Neck',
    'RightArm', 'RightForeArm', 'RightHand',
    'LeftArm', 'LeftForeArm', 'LeftHand',
    'RightUpLeg', 'RightLeg', 'RightFoot',
    'LeftUpLeg', 'LeftLeg', 'LeftFoot',
    'eye_end_r', 'eye_end_l',
    'ear_r', 'ear_l',
}
# to list format as (name, name, '')
pose_parts = [(name.lower(), name, '') for name in pose_parts]


armature = list_armatures(visible_only=True)[0]

# get the bone position in world space
def get_bone_pos_global(armature, bone_name):
    bone = armature.pose.bones[bone_name]
    bone_pos = armature.matrix_world @ bone.head
    return bone_pos


# make camera look at the bone
def look_at(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = (point - loc_camera).to_track_quat('-Z', 'Y')
    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()


# set distance between camera and bone
def set_distance(obj_camera, point, distance):
    loc_camera = obj_camera.matrix_world.to_translation()
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = (point - loc_camera).to_track_quat('-Z', 'Y')
    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()
    # set distance
    obj_camera.location = point + rot_quat @ Vector((0.0, 0.0, distance))


# custom operator
class BatchRenderOperator(bpy.types.Operator):
    bl_idname = 'opr.custom_operator'
    bl_label = 'Render'

    def execute(self, context):
        time_start = time.time()

        # gen 10000 random numbers
        for i in range(10000):
            # caclulate cosin and sin
            cos = math.cos(i)
            sin = math.sin(i)

        # report time cost
        time_cost = time.time() - time_start
        self.report({'INFO'}, 'Time cost: {:.2f} seconds'.format(time_cost))
        
        # print focus on
        focus_on = context.scene['focus on']
        # get enum value
        focus_on = context.scene.bl_rna.properties['focus on'].enum_items[focus_on].name
        print(focus_on)

        return {'FINISHED'}


class PreviewPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_preview_panel'
    bl_label = 'Preview'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        col = self.layout.column()

        col.label(text="Focus On")
        for (prop_name, _) in FOCUS_PROPS:
            col.row().prop(context.scene, prop_name)

        # file save part
        col.separator()
        col.label(text="File")
        for (prop_name, _) in FILE_PROPS:
            col.row().prop(context.scene, prop_name)

        # camera part
        col.separator()
        col.label(text="Camera")
        for (prop_name, _) in CAM_PROPS:
            col.row().prop(context.scene, prop_name)

        # divider
        col.separator()
        col.label(text="Debug")
        # button to render
        col.operator('render.render', icon='RENDER_STILL')

        # batch render part
        col.separator()
        col.label(text="Batch Render")
        for (prop_name, _) in BATCH_PROPS:
            col.row().prop(context.scene, prop_name)
        # custom button
        col.operator('opr.custom_operator')


def get_selected_bone(context):
    value = context.scene['focus on']
    if value == 0:
        value = random.choice(range(1, len(pose_parts)))

    bone_name = context.scene.bl_rna.properties['focus on'].enum_items[value].name
    # print(bone_name)
    return bone_name


def set_value(context, value):
    context.scene['max scope'] = max(context.scene['min scope'], context.scene['max scope'])
    context.scene['min scope'] = min(context.scene['min scope'], context.scene['max scope'])
    vec = get_bone_pos_global(armature, get_selected_bone(context))
    set_distance(bpy.data.objects['Camera'], vec, value)


CLASSES = [
    PreviewPanel,
    BatchRenderOperator,
]

FOCUS_PROPS = [
    ('focus on', bpy.props.EnumProperty(
        name='Bones',
        items=[('random', 'Random', '')] + pose_parts,
        default='random',
        # add event handler
        update=lambda self, context: set_value(context, context.scene['max scope'])
    )),
]

FILE_PROPS = [
    ('is save', bpy.props.BoolProperty(name='Save', default=False)),
    ('dir path', bpy.props.StringProperty(name='Directory Path', default='', subtype='DIR_PATH', options={'HIDDEN'})),
]

CAM_PROPS = [
    # bool to enable/disable motion blur
    ('is motion blur', bpy.props.BoolProperty(name='Motion Blur', default=False)),
    ('min scope', bpy.props.FloatProperty(
        name='Min Distance', default=0.1, min=0.1, max=10.0,
        # add event handler
        update=lambda self, context: set_value(context, context.scene['min scope'])
    )),
    ('max scope', bpy.props.FloatProperty(
        name='Max Distance', default=1.0, min=0.1, max=10.0,
        # add event handler
        update=lambda self, context: set_value(context, context.scene['max scope'])
    )),
    # deviate from the center
    ('deviation', bpy.props.FloatProperty(
        name='Deviation', default=0.0, min=0.0, max=1.0,
        description='Deviate from the center',
    )),
]

BATCH_PROPS = [
    ('amount', bpy.props.IntProperty(name='Amount', default=10, min=1)),
]

TOTAL_PROPS = [
    FOCUS_PROPS,
    FILE_PROPS,
    CAM_PROPS,
    BATCH_PROPS,
]

TOTAL_PROPS = [item for sublist in TOTAL_PROPS for item in sublist]


def register():
    # stack PROPS and BATCH_PROPS
    for (prop_name, prop_value) in TOTAL_PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)
    
    for klass in CLASSES:
        bpy.utils.register_class(klass)


def unregister():
    for (prop_name, _) in TOTAL_PROPS:
        delattr(bpy.types.Scene, prop_name)

    for klass in CLASSES:
        bpy.utils.unregister_class(klass)


if __name__ == '__main__':
    register()
    # unregister()
