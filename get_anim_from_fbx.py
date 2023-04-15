import bpy
import os
import mathutils
import math






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
    # delete object image
    for img in bpy.data.images:
        bpy.data.images.remove(img)
    # return animation name
    return fbx_name


if __name__ == "__main__":
    f_path = "D:\\projects\\HCD_AI_blender_ver\\anim\\Pointing.fbx"

    anims = load_anim(f_path)
    # armas = show_armature()
