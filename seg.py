import bpy
import random


class SynthSeg():
    def __init__(self, num, debug=False):
        self.num = num
        self.debug = debug

    def render(self):
        # get scene
        scene = bpy.context.scene
        node_sets = scene.node_tree.nodes
        scene.use_nodes = True

        for i in range(self.num):
            # random flip axis
            node_sets["flip"].axis = random.choice(["X", "Y", "XY"])
            # random angle in degrees [0, 90, 180, 270]
            angle = random.choice([0, 90, 180, 270])
            # set rotation angle
            node_sets["angle of rotation"].outputs[0].default_value = float(angle)
            # render and save
            if not self.debug:
                bpy.ops.render.render(write_still=True)
                print("rendering image: ", i)


if __name__ == "__main__":
    SynthSeg(1, debug=True).render()
