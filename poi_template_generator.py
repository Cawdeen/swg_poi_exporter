import bpy
from pathlib import Path

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
SERVER_PATH = Path(r"D:\r3git\dsrc\sku.0\sys.server\compiled\game\object\building\poi")
SHARED_PATH = Path(r"D:\r3git\dsrc\sku.0\sys.shared\compiled\game\object\building\poi")

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def has_mif_objects(col):
    """Return True if collection has any object valid for MIF export."""
    for o in col.all_objects:
        if o.type == 'LIGHT' and getattr(o.data, "type", None) == 'POINT':
            return True
        if str(o.get("type", "")).upper() == "CHLD":
            return True
    return False

def has_poi_objects(col):
    """Return True if collection has any object valid for POI export."""
    for o in col.all_objects:
        if "TEMPLATE" in o.keys():
            return True
    return False

# ------------------------------------------------------------
# TEMPLATE BUILDERS
# ------------------------------------------------------------
def build_server_template(collection_name):
    return f"""@base object/building/poi/base/base_poi_building_egg.iff

@class building_object_template 1
@class tangible_object_template 3
@class object_template 8

sharedTemplate = "object/building/poi/shared_{collection_name}.iff"

objvars = [
\t"theater" = [
\t\t"tbl" = "datatables/poi/{collection_name}.iff",
\t\t"spawnMethod" = 1,
\t\t"persist" = 1]]
"""

def build_shared_template(collection_name):
    return f"""@base  object/building/poi/base/shared_base_poi_building.iff

@class building_object_template 1

terrainModificationFileName = "terrain/poi_medium.lay"

@class tangible_object_template 7
@class object_template 7

clientDataFile = "clientdata/poi/shared_{collection_name}.cdf"
"""

# ------------------------------------------------------------
# OPERATOR
# ------------------------------------------------------------
class EXPORT_SCENE_OT_generate_poi_templates(bpy.types.Operator):
    """Generate SWG POI shared and server templates from the active collection"""
    bl_idname = "export_scene.poi_templates"
    bl_label = "Generate SWG POI Templates (.iff)"

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc:
            self.report({'ERROR'}, "No active collection selected.")
            return {'CANCELLED'}

        col = alc.collection
        name = col.name.strip()

        has_mif = has_mif_objects(col)
        has_poi = has_poi_objects(col)

        if not (has_mif and has_poi):
            msg = f"Collection '{name}' missing required objects: "
            if not has_mif:
                msg += "no MIF-type (LIGHT or CHLD) objects. "
            if not has_poi:
                msg += "no POI-type (TEMPLATE) objects. "
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}

        server_text = build_server_template(name)
        shared_text = build_shared_template(name)

        SERVER_PATH.mkdir(parents=True, exist_ok=True)
        SHARED_PATH.mkdir(parents=True, exist_ok=True)

        server_file = SERVER_PATH / f"{name}.iff"
        shared_file = SHARED_PATH / f"shared_{name}.iff"

        server_file.write_text(server_text, encoding="utf-8")
        shared_file.write_text(shared_text, encoding="utf-8")

        self.report({'INFO'}, f"Templates created for '{name}'")
        return {'FINISHED'}

# ------------------------------------------------------------
# MENU + REGISTRATION
# ------------------------------------------------------------
def menu_func_export(self, context):
    self.layout.operator(EXPORT_SCENE_OT_generate_poi_templates.bl_idname, text="SWG POI Templates (.iff)")

def register():
    bpy.utils.register_class(EXPORT_SCENE_OT_generate_poi_templates)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(EXPORT_SCENE_OT_generate_poi_templates)
