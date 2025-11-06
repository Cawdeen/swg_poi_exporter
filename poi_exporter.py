bl_info = {
    "name": "Export Collection to SWG Table",
    "author": "Collin Farrell",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "File > Export",
    "description": "Exports all mesh/empty objects in the active collection to SWG coordinate table using TEMPLATE property. Auto-saves to datatables\\poi\\shatterpoint",
    "category": "Import-Export",
}

import bpy
import math
from pathlib import Path

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
EXPORT_DIR = Path(r"D:\r3git\dsrc\sku.0\sys.server\compiled\game\datatables\poi")

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

        template = o.get("TEMPLATE", None)
        if not template:
            continue  # skip objects without TEMPLATE property
        rows.append(f"{template}\t{f2(swg_x)}\t{f2(swg_y)}\t{f2(swg_z)}\t{f2(swg_yaw)}")

    return rows

# ------------------------------------------------------------
# operator
# ------------------------------------------------------------
class EXPORT_SCENE_OT_collection_swgtable(bpy.types.Operator):
    """Export active collection to SWG coordinate table (auto path)"""
    bl_idname = "export_scene.collection_swgtable"
    bl_label = "Collection → SWG Table (.tab)"

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

        # Build auto output path
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = EXPORT_DIR / f"{col.name}.tab"

        # Write file
        with open(out_path, "w", encoding="utf-8") as f:
            # Header row
            f.write("TEMPLATE\tX\tY\tZ\tYAW\n")
            # Column types (s = string, f = float)
            f.write("s\tf\tf\tf\tf\n")
            # Data rows
            f.write("\n".join(rows))
            f.write("\n")  # ensure trailing newline

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
