import bpy
import os
import math

bl_info = {
    "name": "Circle Renderer",
    "description": "Render 8 angle of selected objects with the setup that include in folder",
    "author": "yigitkanat",
    "version": (0, 0, 1),
    "blender": (3, 4, 1),
    "location": "3D View > Circle Renderer",
    "category": "Development"
}

from bpy.props import (StringProperty,
                       IntProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )


def render8directions_selected_objects(path, res, action):
    # path fixing
    path = os.path.abspath(path)

    # get list of selected objects
    selected_list = bpy.context.selected_objects

    # deselect all in scene
    bpy.ops.object.select_all(action='TOGGLE')

    s = bpy.context.scene

    s.render.resolution_x = res  # set to whatever you want!
    s.render.resolution_y = res

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
            if (a.name == action):

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



class RenderProperties(PropertyGroup):
    my_int: IntProperty(
        name="Resolution",
        description="Resolution",
        default=512,
        min=10,
        max=9999
    )

    my_path: StringProperty(
        name="Output Directory",
        description="Choose a output directory:",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    my_action: StringProperty(
        name="Action Name",
        description="Name of the export action",
        default="run",
        maxlen=1024,
    )

class WM_OT_Export(Operator):
    bl_label = "Export"
    bl_idname = "wm.export"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        render8directions_selected_objects(mytool.my_path,mytool.my_int,mytool.my_action)
        return {'FINISHED'}

class OBJECT_PT_CustomPanel(Panel):
    bl_label = "Circle Renderer"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Circle Renderer"
    bl_context = "objectmode"

    @classmethod
    def poll(self, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.prop(mytool, "my_action")
        layout.prop(mytool, "my_int")
        layout.prop(mytool, "my_path")

        layout.operator("wm.export")

        layout.separator()


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    RenderProperties,
    WM_OT_Export,
    OBJECT_PT_CustomPanel
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=RenderProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()


