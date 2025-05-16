import bpy
import rna_keymap_ui

addon_keymaps = []

def FindConflict(box, operator_idname):
    ku = bpy.context.window_manager.keyconfigs.user
    km_names = ['3D View', '3D View Generic', 'Object Mode', 'Mesh', 'Curve']
    target_kmi = None

    # Search in all keymaps for the operator
    for km_name in km_names:
        km = ku.keymaps.get(km_name)
        if not km:
            continue
        for kmi in km.keymap_items:
            if kmi.idname == operator_idname:
                target_kmi = kmi
                break
        if target_kmi:
            break

    if not target_kmi:
        return 

    # Now find conflicts (also check only active hotkey)
    for km_name in km_names:
        km = ku.keymaps.get(km_name)
        if not km:
            continue
        for kmi in km.keymap_items:
            if (kmi.active and
                kmi.type == target_kmi.type and
                kmi.ctrl == target_kmi.ctrl and
                kmi.alt == target_kmi.alt and
                kmi.shift == target_kmi.shift and
                kmi.idname != operator_idname):
                col = box.column()
                col.label(text=f'Conflict hotkey: 3D View → {km_name} → {kmi.name}')
                col.prop(kmi, 'active')

def store_snap_settings(context):
    ts = context.scene.tool_settings
    return {
        'use_snap': ts.use_snap,
        'snap_elements': ts.snap_elements.copy(),
        'snap_target': ts.snap_target,
        'use_snap_align_rotation': ts.use_snap_align_rotation
    }

def restore_snap_settings(context, settings):
    ts = context.scene.tool_settings
    ts.use_snap = settings['use_snap']
    ts.snap_elements = settings['snap_elements']
    ts.snap_target = settings['snap_target']
    ts.use_snap_align_rotation = settings['use_snap_align_rotation']

class OBJECT_OT_Snap_to_grid(bpy.types.Operator):
    bl_idname = "view3d.snap_to_grid"
    bl_label = "Snap To Grid"

    def modal(self, context, event):
        if event.type == self.key and event.value == 'RELEASE':
            restore_snap_settings(context, self.snap_settings)
            return {'FINISHED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.key = event.type
        self.snap_settings = store_snap_settings(context)

        ts = context.scene.tool_settings
        ts.use_snap = True
        ts.snap_elements = {'GRID'}
        ts.snap_target = 'ACTIVE'
        ts.use_snap_align_rotation = False

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class OBJECT_OT_Snap_to_vertex(bpy.types.Operator):
    bl_idname = "view3d.snap_to_vertex"
    bl_label = "Snap To Vertex"

    def modal(self, context, event):
        if event.type == self.key and event.value == 'RELEASE':
            restore_snap_settings(context, self.snap_settings)
            return {'FINISHED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.key = event.type
        self.snap_settings = store_snap_settings(context)

        ts = context.scene.tool_settings
        ts.use_snap = True
        ts.snap_elements = {'VERTEX'}
        ts.snap_target = 'ACTIVE'
        ts.use_snap_align_rotation = False

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class Snap_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        box = layout.row().box()
        FindConflict(box, "view3d.snap_to_grid")
        box = layout.row().box()

        box2 = layout.row().box()
        FindConflict(box2, "view3d.snap_to_vertex")
        box2 = layout.row().box()

        ku = bpy.context.window_manager.keyconfigs.user
        km = ku.keymaps.get('3D View')

        kmi = km.keymap_items.get('view3d.snap_to_grid')
        rna_keymap_ui.draw_kmi([], ku, km, kmi, box, 0)
        
        kmi2 = km.keymap_items.get('view3d.snap_to_vertex')
        rna_keymap_ui.draw_kmi([], ku, km, kmi2, box2, 0)

classes = [
    OBJECT_OT_Snap_to_grid,
    OBJECT_OT_Snap_to_vertex,
    Snap_Preferences
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager
    kc=wm.keyconfigs.addon

    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        akmi = km.keymap_items.new('view3d.snap_to_vertex', type = 'V', value = 'PRESS', ctrl = False, shift = False)
        addon_keymaps.append((km, akmi))
        akmi2 = km.keymap_items.new('view3d.snap_to_grid', type = 'X', value = 'PRESS', ctrl = False, shift = False)
        addon_keymaps.append((km, akmi2))

def unregister():
    for km, kmi in addon_keymaps:
        if km and kmi:
            try:
                km.keymap_items.remove(kmi)
            except:
                pass 
    addon_keymaps.clear()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
