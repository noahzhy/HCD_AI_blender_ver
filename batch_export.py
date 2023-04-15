# exports each selected object into its own file

import bpy
import os

# export to blend file location
basedir = os.path.dirname(bpy.data.filepath)

if not basedir:
    raise Exception("Blend file is not saved")

view_layer = bpy.context.view_layer

obj_active = view_layer.objects.active
selection = bpy.context.selected_objects

obj = selection[0]
view_layer.objects.active = obj

name = bpy.path.clean_name(obj.name)
fn = os.path.join(basedir, name)


bone_dict = {
    'thumb_end_r': 'RightHandThumb4', 'thumb_end_l': 'LeftHandThumb4',
    'index_end_r': 'RightHandIndex4', 'index_end_l': 'LeftHandIndex4',
    'middle_end_r': 'RightHandMiddle4', 'middle_end_l': 'LeftHandMiddle4',
    'ring_end_r': 'RightHandRing4', 'ring_end_l': 'LeftHandRing4',
    'pinky_end_r': 'RightHandPinky4', 'pinky_end_l': 'LeftHandPinky4',
}
    


# function to rename bones via given object name, and dictionary of bones
def rename_bones(obj_name, bone_dict):
    for bone in bpy.data.objects[obj_name].pose.bones:
        if bone.name in bone_dict.keys():
            bone.name = bone_dict[bone.name]


rename_bones(obj.name, bone_dict)

bpy.ops.export_scene.fbx(
    filepath=fn + ".fbx",
    # path_mode='COPY',
    # embed_textures=True,
    object_types={'ARMATURE', 'MESH', 'EMPTY'},
    use_selection=True,
    axis_forward='Y',
    axis_up='Z',
    apply_unit_scale=True,
    armature_nodetype='ROOT',
    use_armature_deform_only=True,
    bake_anim=False,
)

# Can be used for multiple formats
# bpy.ops.export_scene.x3d(filepath=fn + ".x3d", use_selection=True)
print("written:", fn)


view_layer.objects.active = obj_active

