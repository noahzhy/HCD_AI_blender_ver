# function to get bone position via given armature name, bone name
def get_bone_pos(bone_name):
    for armas in list_armatures(visible_only=True):
        bpy.data.objects[armas.name].select_set(True)
        for bone in armas.pose.bones:
            # get global position in 3d space
            if bone.name == bone_name:
                mv = armas.convert_space(pose_bone=bone, matrix=bone.matrix, from_space='POSE', to_space='WORLD')
                print(bone.name, mv.to_translation())
                return mv.to_translation()