import bpy
import bpy_extras
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


armature = bpy.data.objects["metarig"]
camera = bpy.data.objects["Camera"]
empty = bpy.data.objects["Empty"]


# function to get bone position
def get_bone_pos_global(armature, bone_name):
    bone = armature.pose.bones[bone_name]
    bone_pos = armature.matrix_world @ bone.head
    return bone_pos


def occlusion_ray(scene, dg, origin, direction, distance=1000):
    direction.normalized()
    is_hit, loc, _, index, hit_obj, _ = scene.ray_cast(
        dg,
        origin,
        direction,
        distance=distance
    )

    if is_hit:
        empty.location = loc
        return is_hit, hit_obj.name_full, index
    else:
        return is_hit, None, None


def is_occluded(camera, boneVec, threshold=10):
    # get current scene
    scene = bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    # get vectors which define view frustum of camera
    _, _, _, top_left = camera.data.view_frame(scene=scene)

    # convert [0, 1] to [-.5, .5]
    x, y, _ = world_to_camera_view(scene, camera, boneVec)
    pixel_vector = Vector((x-.5, y-.5, top_left[2]))
    pixel_vector.rotate(camera.matrix_world.to_quaternion())

    # camera -> bone
    c2b = occlusion_ray(scene, dg, camera.matrix_world.translation, pixel_vector, 1000)
    # bone -> camera
    b2c = occlusion_ray(scene, dg, boneVec, -pixel_vector, threshold)

    if c2b[0] and b2c[0]:
        return (c2b != b2c)
    else:
        return True


if __name__ == '__main__':
    print("======================= occlusion test =======================")

    b_name = "eye"
    boneVec = get_bone_pos_global(armature, b_name)
    if is_occluded(camera, boneVec, .1):
        print("{} occluded".format(b_name))
    else:
        print("{} not occluded".format(b_name))    
