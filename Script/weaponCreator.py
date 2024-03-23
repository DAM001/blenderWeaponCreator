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
from bpy_extras.io_utils import ExportHelper

#####################################################################

class VIEW3D_PT_CustomPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Weapon Creator"
    bl_label = "Weapon Creator by DAM"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(icon="BLENDER", text="Modular weapon builder by DAM")
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
        col.label(icon="INFO", text=f"Selected: {weapon_base_objects[weapon_base_index]}")
        col.operator("object.set_base_logic", text="Change base")

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
            bpy.data.objects[obj_name].hide_render = True
        bpy.data.objects[weapon_base_objects[weapon_base_index]].hide_set(False)
        bpy.data.objects[weapon_base_objects[weapon_base_index]].hide_render = False

        #update other components on base change cos the size difference
        update_barrel_position()
        update_scope_position_on_change(context)
        update_buttstock_position()
        update_magazine_position_on_change(context)

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
        current_barrel = "None" if weapon_barrel_index >= len(weapon_barrel_objects) else weapon_barrel_objects[weapon_barrel_index]
        col.label(icon="INFO", text=f"Selected: {current_barrel}")
        col.operator("object.set_barrel_logic", text="Change Barrel")

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
                bpy.data.objects[obj_name].hide_render = True
        
        # Show the next barrel if it's not the "None" option
        if weapon_barrel_index < len(weapon_barrel_objects):
            bpy.data.objects[weapon_barrel_objects[weapon_barrel_index]].hide_set(False)
            bpy.data.objects[weapon_barrel_objects[weapon_barrel_index]].hide_render = False

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
        current_scope = "None" if weapon_scope_index >= len(weapon_scope_objects) else weapon_scope_objects[weapon_scope_index]
        col.label(icon="INFO", text=f"Selected: {current_scope}")
        col.prop(context.object, "weapon_scope_position", slider=True)
        col.operator("object.set_scope_logic", text="Change Scope")

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
                bpy.data.objects[obj_name].hide_render = True
        
        # Show the next scope if it's not the "None" option
        if weapon_scope_index < len(weapon_scope_objects):
            active_scope = bpy.data.objects[weapon_scope_objects[weapon_scope_index]]
            active_scope.hide_set(False)
            active_scope.hide_render = False
            active_scope.location.y = weapon_scope_current_position

        return {'FINISHED'}

#####################################################################

weapon_buttstock_objects = ['ButtstockSmall', 'ButtstockMedium']
weapon_buttstock_index = 0
weapon_buttstock_positions = [-0.3, -0.3, -0.5]
weapon_buttstock_current_position = 0

def update_buttstock_position():
    if weapon_buttstock_index < len(weapon_buttstock_objects):
        active_buttstock = bpy.data.objects[weapon_buttstock_objects[weapon_buttstock_index]]
        active_buttstock.location.y = weapon_buttstock_positions[weapon_base_index] + weapon_buttstock_current_position

def update_buttstock_position_logic(self, context):
    global weapon_buttstock_current_position
    weapon_buttstock_current_position = self.weapon_buttstock_position
    update_buttstock_position()

bpy.types.Object.weapon_buttstock_position = bpy.props.FloatProperty(
    name="Position",
    description="Change the position of the buttstock",
    default=0,
    min=0,
    max=1,
    update=update_buttstock_position_logic
)

class SetButtstockPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Weapon Creator"
    bl_label = "Buttstock"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        buttstock_text = "None" if weapon_buttstock_index >= len(weapon_buttstock_objects) else weapon_buttstock_objects[weapon_buttstock_index]
        col.label(icon="INFO", text=f"Selected: {buttstock_text}")
        col.prop(context.object, "weapon_buttstock_position", slider=True)
        col.operator("object.set_buttstock_logic", text="Change Buttstock")

class SetButtstockLogic(bpy.types.Operator):
    """Select a part as the buttstock of the weapon"""
    bl_idname = "object.set_buttstock_logic"
    bl_label = "Set Buttstock Logic"

    def execute(self, context):
        global weapon_buttstock_index
        weapon_buttstock_index = (weapon_buttstock_index + 1) % (len(weapon_buttstock_objects) + 1)  # +1 for the "None" option
        
        # Hide all buttstocks first
        for obj_name in weapon_buttstock_objects:
            if obj_name in bpy.data.objects:
                bpy.data.objects[obj_name].hide_set(True)
                bpy.data.objects[obj_name].hide_render = True
        
        # Show the next buttstock if it's not the "None" option
        if weapon_buttstock_index < len(weapon_buttstock_objects):
            active_buttstock = bpy.data.objects[weapon_buttstock_objects[weapon_buttstock_index]]
            active_buttstock.hide_set(False)
            active_buttstock.hide_render = False
            update_buttstock_position()

        return {'FINISHED'}
    
#####################################################################
    
weapon_magazine_objects = ['MagazineSmall', 'MagazineMedium', 'MagazineBig']
weapon_magazine_index = 0

weapon_magazine_current_position = 0.1
weapon_magazine_minimum_positions = [0.5, 0.5, 0.5]
weapon_magazine_maximum_positions = [0.7, 1.2, 1.5]

def update_magazine_position(self, context):
    global weapon_magazine_index
    global weapon_magazine_current_position

    active_magazine_name = weapon_magazine_objects[weapon_magazine_index]
    active_magazine = bpy.data.objects.get(active_magazine_name)

    if active_magazine:
        weapon_magazine_current_position = context.object.weapon_magazine_position
        active_magazine.location.y = weapon_magazine_current_position

def update_magazine_position_on_change(context):
    update_weapon_magazine_property(weapon_magazine_minimum_positions[weapon_base_index], weapon_magazine_maximum_positions[weapon_base_index])

    global weapon_magazine_current_position
    if (weapon_magazine_index < len(weapon_magazine_objects)):
        active_magazine_name = weapon_magazine_objects[weapon_magazine_index]
        active_magazine = bpy.data.objects.get(active_magazine_name)

        if active_magazine:
            context.object.weapon_magazine_position = weapon_magazine_current_position
            active_magazine.location.y = weapon_magazine_current_position

def update_weapon_magazine_property(min_value, max_value):
    def get_weapon_magazine_position(self):
        return self.get('weapon_magazine_position', min_value)

    def set_weapon_magazine_position(self, value):
        self['weapon_magazine_position'] = max(min(value, max_value), min_value)
    
    bpy.types.Object.weapon_magazine_position = bpy.props.FloatProperty(
        name="Position",
        description="Change the position of the magazine",
        default=min_value,
        min=min_value,
        max=max_value,
        get=get_weapon_magazine_position,
        set=set_weapon_magazine_position,
        update=update_magazine_position
    )

update_weapon_magazine_property(weapon_magazine_minimum_positions[weapon_base_index], weapon_magazine_maximum_positions[weapon_base_index])

class SetMagazinePanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Weapon Creator"
    bl_label = "Magazine"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        current_magazine = "None" if weapon_magazine_index >= len(weapon_magazine_objects) else weapon_magazine_objects[weapon_magazine_index]
        col.label(icon="INFO", text=f"Selected: {current_magazine}")
        col.prop(context.object, "weapon_magazine_position", slider=True)
        col.operator("object.set_magazine_logic", text="Change Magazine")

class SetMagazineLogic(bpy.types.Operator):
    """Change the type of the magazine"""
    bl_idname = "object.set_magazine_logic"
    bl_label = "Set Magazine Logic"

    def execute(self, context):
        global weapon_magazine_index
        global weapon_magazine_current_position
        
        weapon_magazine_index = (weapon_magazine_index + 1) % (len(weapon_magazine_objects) + 1)  # +1 for "None" option
        
        for obj_name in weapon_magazine_objects:
            if obj_name in bpy.data.objects:
                bpy.data.objects[obj_name].hide_set(True)
                bpy.data.objects[obj_name].hide_render = True
        
        if weapon_magazine_index < len(weapon_magazine_objects):
            active_magazine = bpy.data.objects[weapon_magazine_objects[weapon_magazine_index]]
            active_magazine.hide_set(False)
            active_magazine.hide_render = False
            active_magazine.location.y = weapon_magazine_current_position

        return {'FINISHED'}

    
#####################################################################

class SaveFinalProduct(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Weapon Creator"
    bl_label = "Save Model"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("object.save_final_product_image", text="Create Icon Image")
        col.operator("object.save_final_product", text="Save Model")

class SaveFinalProductImage(bpy.types.Operator, ExportHelper):
    """Create an icon image from the weapon"""
    bl_idname = "object.save_final_product_image"
    bl_label = "Export Weapon Icon"
    filename_ext = ".png"

    filter_glob: bpy.props.StringProperty(
        default='*.png',
        options={'HIDDEN'}
    )

    def toggle_objects_visibility(self, objects_names, visibility):
        for obj_name in objects_names:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                obj.hide_render = not visibility

    def execute(self, context):
        camera_name = 'Camera'
        light_name = 'Light'
        
        # Ensure the scene uses RGBA to support transparency
        context.scene.render.image_settings.color_mode = 'RGBA'
        context.scene.render.filepath = self.filepath
        
        # Toggle the visibility of the camera and light
        self.toggle_objects_visibility([camera_name, light_name], True)
        
        # Render the scene
        bpy.ops.render.render(write_still=True)
        
        # Toggle the visibility of the camera and light back
        self.toggle_objects_visibility([camera_name, light_name], False)

        return {'FINISHED'}

class SaveFinalProductLogic(bpy.types.Operator, ExportHelper):
    """Save the final product as an '.fbx' file"""
    bl_idname = "object.save_final_product"
    bl_label = "Export Weapon"
    filename_ext = ".fbx"

    filter_glob: bpy.props.StringProperty(
        default='*.fbx',
        options={'HIDDEN'},
    )

    def execute(self, context):
        output_path = self.filepath

        # Filter visible objects
        visible_objects = [obj for obj in context.view_layer.objects if obj.visible_get() and obj.type == 'MESH']
        initial_active = context.view_layer.objects.active
        initial_selection = [obj for obj in context.selected_objects]

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Select visible objects
        for obj in visible_objects:
            obj.select_set(True)

        # Export the selected visible objects to FBX
        bpy.ops.export_scene.fbx(filepath=output_path, use_selection=True)

        # Restore initial selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in initial_selection:
            obj.select_set(True)
        context.view_layer.objects.active = initial_active

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

    bpy.utils.register_class(SetButtstockPanel)
    bpy.utils.register_class(SetButtstockLogic)

    bpy.utils.register_class(SetMagazinePanel)
    bpy.utils.register_class(SetMagazineLogic)

    bpy.utils.register_class(SaveFinalProduct)
    bpy.utils.register_class(SaveFinalProductImage)
    bpy.utils.register_class(SaveFinalProductLogic)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_CustomPanel)
    bpy.utils.unregister_class(ClearSceneView)

    bpy.utils.unregister_class(SetBasePanel)
    bpy.utils.unregister_class(SetBaseLogic)

    bpy.utils.unregister_class(SetBarrelPanel)
    bpy.utils.unregister_class(SetBarrelLogic)

    bpy.utils.unregister_class(SetScopePanel)
    bpy.utils.unregister_class(SetScopeLogic)

    bpy.utils.unregister_class(SetButtstockPanel)
    bpy.utils.unregister_class(SetButtstockLogic)

    bpy.utils.unregister_class(SetMagazinePanel)
    bpy.utils.unregister_class(SetMagazineLogic)

    bpy.utils.unregister_class(SaveFinalProduct)
    bpy.utils.unregister_class(SaveFinalProductImage)
    bpy.utils.unregister_class(SaveFinalProductLogic)

if __name__ == "__main__":
    register()