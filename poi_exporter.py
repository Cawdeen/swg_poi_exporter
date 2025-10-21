bl_info = {
    "name": "Export Collection to SWG Table",
    "author": "Collin Farrell",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "File > Export",
    "description": "Exports all mesh objects in the active collection (and sub-collections) to SWG coordinate table using object property TEMPLATE",
    "category": "Import-Export",
}

import bpy
import math
from bpy_extras.io_utils import ExportHelper
from pathlib import Path

# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------
def f2(x: float) -> str:
    return f"{float(x):.2f}"

def get_cp(obj, name, default):
    """Read custom property safely"""
    return obj.get(name, default)

def iter_collection_objects(col, recursive=True):
    """Yield every object in collection and sub-collections once"""
    seen = set()
    def walk(c):
        for o in c.objects:
            if o.name not in seen:
                seen.add(o.name)
                yield o
        if recursive:
            for cc in c.children:
                yield from walk(cc)
    yield from walk(col)

# ------------------------------------------------------------
# exporter core
# ------------------------------------------------------------
def build_table_for_collection(col):
    rows = []
    for o in iter_collection_objects(col, recursive=True):
        if o.type not in {"MESH", "EMPTY"}:
            continue

        # Blender → SWG
        swg_x = o.location.x
        swg_y = o.location.z     # Blender Z → SWG Y
        swg_z = o.location.y     # Blender Y → SWG Z
        swg_yaw = -math.degrees(o.rotation_euler.z)

        template = str(get_cp(o, "TEMPLATE", o.name))
        rows.append(f"{template}\t{f2(swg_x)}\t{f2(swg_y)}\t{f2(swg_z)}\t{f2(swg_yaw)}")

    return rows

# ------------------------------------------------------------
# operator
# ------------------------------------------------------------
class EXPORT_SCENE_OT_collection_swgtable(bpy.types.Operator, ExportHelper):
    """Export active collection (and sub-collections) to SWG coordinate table"""
    bl_idname = "export_scene.collection_swgtable"
    bl_label = "Collection → SWG Table (.txt)"
    filename_ext = ".txt"

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc:
            self.report({'ERROR'}, "No active collection selected in Outliner.")
            return {'CANCELLED'}
        col = alc.collection

        rows = build_table_for_collection(col)
        if not rows:
            self.report({'WARNING'}, f'No valid objects found in "{col.name}".')
            return {'CANCELLED'}

        out_path = Path(self.filepath)
        if out_path.is_dir() or out_path.suffix.lower() != ".txt":
            out_path = out_path / f"{col.name}.txt"

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("TEMPLATE\tX\tY\tZ\tYAW\n")
            f.write("\n".join(rows))

        self.report({'INFO'}, f'Exported {len(rows)} objects from "{col.name}" to "{out_path}".')
        return {'FINISHED'}

# ------------------------------------------------------------
# menu + register
# ------------------------------------------------------------
def menu_func_export(self, context):
    self.layout.operator(EXPORT_SCENE_OT_collection_swgtable.bl_idname, text="Collection → SWG Table (.txt)")

def register():
    bpy.utils.register_class(EXPORT_SCENE_OT_collection_swgtable)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(EXPORT_SCENE_OT_collection_swgtable)

if __name__ == "__main__":
    register()
