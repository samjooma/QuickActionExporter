import bpy
import os

class UIActionList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {"DEFAULT", "COMPACT", "GRID"}:
            row = layout.row(align=True)
            row.alignment = "LEFT"
            row.prop(data=item, property="include_in_export", icon_only=True)
            row.label(text=item.name, icon_value=icon)

class ActionSelectionProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    include_in_export: bpy.props.BoolProperty(default=False)

class QuickAnimationExporterProperties(bpy.types.PropertyGroup):
    actions: bpy.props.CollectionProperty(type=ActionSelectionProperty)
    active_index: bpy.props.IntProperty()

class QuickAnimationExporter(bpy.types.Operator):
    bl_idname = "object.quick_animation_exporter"
    bl_label = "Quick Animation Exporter"
    bl_description = "Description"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(self, context):
        if len(bpy.data.actions) < 1: return False
        if not any((x.type == "ARMATURE" for x in context.selected_objects)): return False
        return True

    def execute(self, context):
        properties = bpy.context.window_manager.quick_animation_exporter
        for action in (bpy.data.actions[x.name] for x in properties.actions if x.include_in_export):
            context.scene.frame_start = round(action.curve_frame_range[0])
            context.scene.frame_end = round(action.curve_frame_range[1])

            directory_path = os.path.dirname(bpy.data.filepath)
            export_path = f"{directory_path}\\{action.name}.fbx"

            for rig_object in (x for x in context.selected_objects if x.type == "ARMATURE"):
                rig_object.animation_data_clear()
                rig_object.animation_data_create()
                rig_object.animation_data.action = action

                bpy.ops.export_scene.fbx(
                    filepath=export_path,
                    use_selection=True,
                    use_visible=True,
                    object_types={"ARMATURE"},
                    add_leaf_bones=False,
                    bake_anim=True,
                    bake_anim_use_all_bones=True,
                    bake_anim_use_nla_strips=False,
                    bake_anim_use_all_actions=False,
                )
        return {"FINISHED"}
    
    def invoke(self, context, event):
        properties = bpy.context.window_manager.quick_animation_exporter
        properties.active_index = 0

        # Remove action properties for actions that don't exist anymore.
        pending_removal = []
        for action_property in properties.actions:
            if action_property.name not in [x.name for x in bpy.data.actions]:
                pending_removal.append(action_property)
        for x in pending_removal:
            properties.actions.remove(x)

        # Add missing actions as new properties.
        for action in bpy.data.actions:
            if action.name not in [x.name for x in properties.actions]:
                new_action_property = properties.actions.add()
                new_action_property.name = action.name
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        properties = bpy.context.window_manager.quick_animation_exporter
        layout.template_list(
            listtype_name="UIActionList",
            list_id="",
            dataptr=properties,
            propname="actions",
            active_dataptr=properties,
            active_propname="active_index",
            type="DEFAULT",
        )

def menu_func(self, context):
    self.layout.operator(QuickAnimationExporter.bl_idname, text=QuickAnimationExporter.bl_label)

classes = (
    UIActionList,
    ActionSelectionProperty,
    QuickAnimationExporterProperties,
    QuickAnimationExporter,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)
    bpy.types.WindowManager.quick_animation_exporter = bpy.props.PointerProperty(type=QuickAnimationExporterProperties)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)
    del bpy.types.WindowManager.quick_animation_exporter
