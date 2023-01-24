import bpy
import random


# get scene
scene = bpy.context.scene
scene.use_nodes = True
node_sets = scene.node_tree.nodes
# random flip axis
node_sets["flip"].axis = random.choice(["X", "Y", "XY"])
# random angle in degrees [0, 90, 180, 270]
angle = random.choice([0, 90, 180, 270])
# set rotation angle
node_sets["angle of rotation"].outputs[0].default_value = float(angle)

# set render output path
# scene.render.filepath = "C:/Users/noahz/Desktop/Seg/test" + "/test" + ".png"

# render and save
bpy.ops.render.render(write_still=True)
