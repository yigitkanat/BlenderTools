import bpy
import os
import math


class MyAddonOperator(bpy.types.Operator):
    bl_idname = "myaddon.my_operator"
    bl_label = "My Operator"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # Do something with the selected file path
        print(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MyAddonPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_myaddon_panel"
    bl_label = "My Addon Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("myaddon.my_operator", text="Select File")

def register():
    bpy.utils.register_class(MyAddonPanel)


def unregister():
    bpy.utils.unregister_class(MyAddonPanel)

if __name__ == "__main__":
    register()

def render8directions_selected_objects(path):
    # path fixing
    path = os.path.abspath(path)

    # get list of selected objects
    selected_list = bpy.context.selected_objects


    # deselect all in scene
    bpy.ops.object.select_all(action='TOGGLE')


    s = bpy.context.scene

    s.render.resolution_x = 256  # set to whatever you want!
    s.render.resolution_y = 256

    # I left this in as in some of my models, I needed to translate the "root" object but
    # the animations were on the armature which I selected.
    #
    # obRoot = bpy.context.scene.objects["root"]

    # loop all initial selected objects (which will likely just be one obect.. I haven't tried setting up multiple yet)
    for o in selected_list:

        # select the object
        bpy.context.scene.objects[o.name].select_set(True)

        scn = bpy.context.scene

        # loop through the actions
        for a in bpy.data.actions:
            # assign the action
            bpy.context.active_object.animation_data.action = bpy.data.actions.get(a.name)

            # dynamically set the last frame to render based on action
            scn.frame_end = int(bpy.context.active_object.animation_data.action.frame_range[1])

            # set which actions you want to render.  Make sure to use the exact name of the action!
            if (
                    #                 a.name == "idle"
                    a.name == "run"
                    #                 or a.name == "dying"
            ):

                # create folder for animation
                action_folder = os.path.join(path, a.name)
                if not os.path.exists(action_folder):
                    os.makedirs(action_folder)

                # loop through all 8 directions
                for angle in range(0, 360, 45):
                    if angle == 0:
                        angleDir = "Front"
                    if angle == 45:
                        angleDir = "FrontRight"
                    if angle == 90:
                        angleDir = "Right"
                    if angle == 135:
                        angleDir = "BackRight"
                    if angle == 180:
                        angleDir = "Back"
                    if angle == 225:
                        angleDir = "BackLeft"
                    if angle == 270:
                        angleDir = "Left"
                    if angle == 315:
                        angleDir = "FrontLeft"

                    # set which angles we want to render.
                    if (
                            angle == 0
                            or angle == 45
                            or angle == 90
                            or angle == 135
                            or angle == 180
                            or angle == 225
                            or angle == 270
                            or angle == 315
                    ):

                        # create folder for specific angle
                        animation_folder = os.path.join(action_folder, angleDir)
                        if not os.path.exists(animation_folder):
                            os.makedirs(animation_folder)

                        # rotate the model for the new angle
                        # bpy.context.active_object.rotation_euler[2] = math.radians(angle)
                        bpy.context.scene.objects['CameraController'].rotation_euler[2] = math.radians(angle);

                        # the below is for the use case where the root needed to be translated.
                        #                        obRoot.rotation_euler[2] = math.radians(angle)

                        # loop through and render frames.  Can set how "often" it renders.
                        # Every frame is likely not needed.  Currently set to 2 (every other).
                        for i in range(s.frame_start, s.frame_end, 1):
                            s.frame_current = i

                            s.render.filepath = (
                                    animation_folder
                                    + "\\"
                                    + str(a.name)
                                    + "_"
                                    + str(angle)
                                    + "_"
                                    + str(s.frame_current).zfill(3)
                            )
                            bpy.ops.render.render(  # {'dict': "override"},
                                # 'INVOKE_DEFAULT',
                                False,  # undo support
                                animation=False,
                                write_still=True
                            )


render8directions_selected_objects('C:\\RenderResult\\Character1')
