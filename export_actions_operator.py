import bpy
import os

class QUICK_ACTION_EXPORT_UL_action_selection(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {"DEFAULT", "COMPACT", "GRID"}:
            row = layout.row(align=True)
            row.alignment = "LEFT"
            row.prop(data=item, property="include_in_export", icon_only=True)
            row.label(text=item.name, icon_value=icon)

class ActionSelectionProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    include_in_export: bpy.props.BoolProperty(default=False)

class QuickActionExportOperator(bpy.types.Operator):
    bl_idname = "export_actions_quick.export"
    bl_label = "Quick action export"
    bl_description = "Export selected actions to FBX files"
    bl_options = {"REGISTER"}

    action_selections: bpy.props.CollectionProperty(type=ActionSelectionProperty)
    active_index: bpy.props.IntProperty()
    name_prefix: bpy.props.StringProperty(
        default="", name="Name prefix", description="Prefix to add before the action name in the file name. Leave this empty to use the name of the selected object"
    )

    @classmethod
    def poll(self, context):
        if len(bpy.data.actions) < 1:
            return False
        selected_armatures = [x for x in context.selected_objects if x.type == "ARMATURE"]
        if len(selected_armatures) < 1:
            return False
        return True

    def execute(self, context):
        selected_armatures = [x for x in context.selected_objects if x.type == "ARMATURE"]
        all_armatures = [x for x in context.scene.objects if x.type == "ARMATURE"]

        # Store current actions.
        old_actions = {}
        for armature in all_armatures:
            if armature.animation_data is None:
                armature.animation_data_create()
            old_actions[armature] = armature.animation_data.action

        for selected_object in selected_armatures:
            for action in (bpy.data.actions[x.name] for x in self.action_selections if x.include_in_export):
                # Set all armatures to use this action.
                for armature in (x for x in context.scene.objects if x.type == "ARMATURE"):
                    armature.animation_data.action = action

                # Export.
                name_prefix = f"{self.name_prefix}_" if self.name_prefix != "" else f"{selected_object.name}_"
                context_override = context.copy()
                context_override["selected_objects"] = [selected_object]
                with context.temp_override(**context_override):
                    context.scene.frame_start = round(action.curve_frame_range[0])
                    context.scene.frame_end = round(action.curve_frame_range[1])
                    directory_path = os.path.dirname(bpy.data.filepath)
                    export_path = f"{directory_path}\\{name_prefix}{action.name}.fbx"
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

        # Restore back to old actions.
        old_actions = {}
        for armature_object in all_armatures:
            try:
                armature_object.animation_data.action = old_actions[armature_object]
            except KeyError:
                armature_object.animation_data.action = None

        return {"FINISHED"}

    def invoke(self, context, event):
        valid_action_names = [x.name for x in bpy.data.actions if x.users > 0]

        # Remove invalid action properties.
        for action_property in (x for x in reversed(self.action_selections) if x.name not in valid_action_names):
            self.action_selections.remove(action_property)

        # Add missing action properties.
        for action_name in valid_action_names:
            if action_name not in (x.name for x in self.action_selections):
                new_action_property = self.action_selections.add()
                new_action_property.name = action_name

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Actions")
        layout.template_list(
            listtype_name="QUICK_ACTION_EXPORT_UL_action_selection",
            list_id="",
            dataptr=self,
            propname="action_selections",
            active_dataptr=self,
            active_propname="active_index",
            type="DEFAULT",
        )
        layout.prop(data=self, property="name_prefix")

def menu_func(self, context):
    self.layout.operator(QuickActionExportOperator.bl_idname, text=QuickActionExportOperator.bl_label)

classes = (
    QUICK_ACTION_EXPORT_UL_action_selection,
    ActionSelectionProperty,
    QuickActionExportOperator,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)
