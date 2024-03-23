bl_info = {
    "name": "Weapon Creator",
    "blender": (4, 0, 0),
    "category": "DAM",
    "description": "Create custom weapons from a modular pack!",
    "author": "DAM",
    "version": (1, 0),
    "location": "View3D > Sidebar > View",
}

import bpy
import math

#####################################################################

class VIEW3D_PT_CustomPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Weapon Creator"
    bl_label = "View"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.lavel(icon="BLENDER", text="Modular weapon builder by DAM")
        #col.operator("object.clear_scene_view", text="Clear Scene View")

# Delete all the objects from the scene
class ClearSceneView(bpy.types.Operator):
    """Remove everything from the current scene"""
    bl_idname = "object.clear_scene_view"
    bl_label = "Clear Scene"
    
    def execute(self, context):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        return {'FINISHED'}

#####################################################################

weapon_base_objects = ['BaseSmall', 'BaseMedium', 'BaseBig']
weapon_base_index = 0

class SetBasePanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Weapon Creator"
    bl_label = "Base"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("object.set_base_logic", text="Change base")
        col.label(icon="INFO", text=f"Selected: {weapon_base_objects[weapon_base_index]}")

class SetBaseLogic(bpy.types.Operator):
    """Select a part as the base of the weapon"""
    bl_idname = "object.set_base_logic"
    bl_label = "Set Base Logic"

    def execute(self, context):
        global weapon_base_index
        visible_obj = None
        
        # Determine the currently visible object, if any
        for obj_name in weapon_base_objects:
            if bpy.data.objects[obj_name].visible_get():
                visible_obj = obj_name
                break
        
        # Find the index of the currently visible object
        if visible_obj:
            current_index = weapon_base_objects.index(visible_obj)
            weapon_base_index = (current_index + 1) % len(weapon_base_objects)
        else:
            weapon_base_index = 0
        
        # Hide all and then show the next object
        for obj_name in weapon_base_objects:
            bpy.data.objects[obj_name].hide_set(True)
        bpy.data.objects[weapon_base_objects[weapon_base_index]].hide_set(False)

        #update other components on base change cos the size difference
        update_barrel_position()
        update_scope_position_on_change(context)

        return {'FINISHED'}
    
#####################################################################

weapon_barrel_objects = ['BarrelSmall', 'BarrelMedium', 'BarrelBig']
weapon_barrel_index = 0

def update_barrel_position():
    if weapon_barrel_index < len(weapon_barrel_objects):
        active_barrel_name = weapon_barrel_objects[weapon_barrel_index]
        active_barrel = bpy.data.objects.get(active_barrel_name)
        
        barrel_positions = [0.9, 1.4, 1.7]
        if active_barrel:
            active_barrel.location.y = barrel_positions[weapon_base_index]

class SetBarrelPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Weapon Creator"
    bl_label = "Barrel"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("object.set_barrel_logic", text="Change Barrel")
        current_barrel = "None" if weapon_barrel_index >= len(weapon_barrel_objects) else weapon_barrel_objects[weapon_barrel_index]
        col.label(icon="INFO", text=f"Selected: {current_barrel}")

class SetBarrelLogic(bpy.types.Operator):
    """Select a barrel for the weapon"""
    bl_idname = "object.set_barrel_logic"
    bl_label = "Set Barrel Logic"

    def execute(self, context):
        global weapon_barrel_index
        
        # Increment the index to show the next barrel, cycle back to 0 after "None"
        weapon_barrel_index = (weapon_barrel_index + 1) % (len(weapon_barrel_objects) + 1) # +1 for the "None" option
        
        # Hide all barrels first
        for obj_name in weapon_barrel_objects:
            if obj_name in bpy.data.objects:
                bpy.data.objects[obj_name].hide_set(True)
        
        # Show the next barrel if it's not the "None" option
        if weapon_barrel_index < len(weapon_barrel_objects):
            bpy.data.objects[weapon_barrel_objects[weapon_barrel_index]].hide_set(False)

        update_barrel_position()

        return {'FINISHED'}

#####################################################################

weapon_scope_objects = ['ScopeSmall', 'ScopeMedium', 'ScopeBig']
weapon_scope_index = 0

weapon_scope_current_position = 0.1
weapon_scope_minimum_positions = [0.1, 0.1, -0.1]
weapon_scope_maximum_positions = [0.5, 1, 1.3]

def update_scope_position(self, context):
    global weapon_scope_index
    global weapon_scope_current_position
    active_scope_name = weapon_scope_objects[weapon_scope_index]
    active_scope = bpy.data.objects.get(active_scope_name)

    if active_scope:
        weapon_scope_current_position = context.object.weapon_scope_position
        active_scope.location.y = weapon_scope_current_position

def update_scope_position_on_change(context):
    update_weapon_scope_property(weapon_scope_minimum_positions[weapon_base_index], weapon_scope_maximum_positions[weapon_base_index])

    global weapon_scope_current_position
    active_scope_name = weapon_scope_objects[weapon_scope_index]
    active_scope = bpy.data.objects.get(active_scope_name)

    if active_scope:
        context.object.weapon_scope_position = weapon_scope_current_position
        active_scope.location.y = weapon_scope_current_position

def update_weapon_scope_property(min_value, max_value):
    def get_weapon_scope_position(self):
        return self.get('weapon_scope_position', min_value)

    def set_weapon_scope_position(self, value):
        self['weapon_scope_position'] = max(min(value, max_value), min_value)
    
    # Redefine the property with the new min and max values
    bpy.types.Object.weapon_scope_position = bpy.props.FloatProperty(
        name="Position",
        description="Change the position of the scope",
        default=min_value,
        min=min_value,
        max=max_value,
        get=get_weapon_scope_position,
        set=set_weapon_scope_position,
        update=update_scope_position
    )

# Initial setup call with the initial min and max values
update_weapon_scope_property(weapon_scope_minimum_positions[weapon_base_index], weapon_scope_maximum_positions[weapon_base_index])

class SetScopePanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Weapon Creator"
    bl_label = "Scope"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(context.object, "weapon_scope_position", slider=True) 
        col.operator("object.set_scope_logic", text="Change Scope")
        current_scope = "None" if weapon_scope_index >= len(weapon_scope_objects) else weapon_scope_objects[weapon_scope_index]
        col.label(icon="INFO", text=f"Selected: {current_scope}")

class SetScopeLogic(bpy.types.Operator):
    """Select a scope for the weapon"""
    bl_idname = "object.set_scope_logic"
    bl_label = "Set Scope Logic"

    def execute(self, context):
        global weapon_scope_index
        global weapon_scope_current_position
        
        # Increment the index to show the next scope, cycle back to 0 after "None"
        weapon_scope_index = (weapon_scope_index + 1) % (len(weapon_scope_objects) + 1) # +1 for the "None" option
        
        # Hide all scopes first
        for obj_name in weapon_scope_objects:
            if obj_name in bpy.data.objects:
                bpy.data.objects[obj_name].hide_set(True)
        
        # Show the next scope if it's not the "None" option
        if weapon_scope_index < len(weapon_scope_objects):
            active_scope = bpy.data.objects[weapon_scope_objects[weapon_scope_index]]
            active_scope.hide_set(False)
            active_scope.location.y = weapon_scope_current_position

        return {'FINISHED'}

#####################################################################

def register():
    bpy.utils.register_class(VIEW3D_PT_CustomPanel)
    bpy.utils.register_class(ClearSceneView)

    bpy.utils.register_class(SetBasePanel)
    bpy.utils.register_class(SetBaseLogic)

    bpy.utils.register_class(SetBarrelPanel)
    bpy.utils.register_class(SetBarrelLogic)

    bpy.utils.register_class(SetScopePanel)
    bpy.utils.register_class(SetScopeLogic)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_CustomPanel)
    bpy.utils.unregister_class(ClearSceneView)

    bpy.utils.unregister_class(SetBasePanel)
    bpy.utils.unregister_class(SetBaseLogic)

    bpy.utils.unregister_class(SetBarrelPanel)
    bpy.utils.unregister_class(SetBarrelLogic)

    bpy.utils.unregister_class(SetScopePanel)
    bpy.utils.unregister_class(SetScopeLogic)

if __name__ == "__main__":
    register()