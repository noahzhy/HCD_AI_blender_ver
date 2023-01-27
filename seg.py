import os
import bpy
import random


class SynthSeg():
    def __init__(self, num, debug=False, outpath=""):
        self.num = num
        self.debug = debug
        self.outpath = outpath
        # init scene
        scene = bpy.context.scene
        scene.use_nodes = True
        self.nodes = scene.node_tree.nodes
        self.nodes["File Output"].base_path = outpath

    def reset(self):
        pass

    def render(self):
        for i in range(self.num):
            # random flip axis
            self.nodes["flip"].axis = random.choice(["X", "Y", "XY"])
            # random angle in degrees [0, 90, 180, 270]
            angle = random.randint(0, 3) * 90
            # set rotation angle
            self.nodes["angle of rotation"].outputs[0].default_value = float(angle)
            # # render and save
            if not self.debug:
                self.render_diff_layer()

            print("rendering folder path: ", os.path.join(self.outpath))

    @staticmethod
    def render_diff_layer(main_viewlayer='ViewLayer', part_viewlayer='ViewLayer_part'):
        # switch to part view layer
        bpy.context.object.modifiers["GeometryNodes"]["Input_2"] = 1
        bpy.ops.render.render(write_still=True, layer=part_viewlayer)
        # switch to view layer
        bpy.context.object.modifiers["GeometryNodes"]["Input_2"] = 0
        bpy.ops.render.render(write_still=True, layer=main_viewlayer)


if __name__ == "__main__":
    output_path = "D:/projects/HCD_AI_blender_ver/data"
    ss = SynthSeg(1, debug=False, outpath=output_path)
    ss.render()
