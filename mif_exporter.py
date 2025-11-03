bl_info = {
    "name": "Export Collection to MIF (LOBJ + CHLD)",
    "author": "You",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "File > Export",
    "description": "Exports POINT lights as LOBJ and CHLD objects to a shared .mif in the SWG clientdata directory",
    "category": "Import-Export",
}

import bpy
from mathutils import Vector
from math import degrees
from pathlib import Path

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
EXPORT_DIR = Path(r"D:\r3git\dsrc\sku.0\sys.client\compiled\game\clientdata\poi")

# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------
def f6(x: float) -> str:
    return f"{float(x):.6f}"

def get_cp(obj, name, default):
    return obj.get(name, default)

# ------------------------------------------------------------
# chunk builders
# ------------------------------------------------------------
def light_to_lobj(obj):
    """POINT light -> LOBJ block. Blender->SWG axis swap for position (Y/Z)."""
    L = obj.data
    m_type = int(get_cp(obj, "type", 1))
    appearance = str(get_cp(obj, "appearance", "appearance/pt_light_generic.prt"))

    # Colors and parameters
    c1 = getattr(L, "color", (1.0, 1.0, 1.0))
    c2 = (
        float(get_cp(obj, "color2_r", 0.0)),
        float(get_cp(obj, "color2_g", 0.0)),
        float(get_cp(obj, "color2_b", 0.0)),
    )

    m_range1 = float(get_cp(obj, "range1", 10.0))
    m_range2 = float(get_cp(obj, "range2", 0.0))
    m_time1  = float(get_cp(obj, "time1", 0.0))
    m_time2  = float(get_cp(obj, "time2", 0.0))
    m_const  = float(get_cp(obj, "constAtten", 0.0))
    m_lin    = float(get_cp(obj, "linearAtten", 0.1))
    m_quad   = float(get_cp(obj, "quadAtten", 0.0))

    # flags
    tod   = int(get_cp(obj, "timeOfDayAware", 0)) & 1
    onoff = int(get_cp(obj, "onOffAware", 0)) & 1
    stateFlags = (tod << 0) | (onoff << 1)

    # position (Blender -> SWG: swap Y/Z)
    p: Vector = obj.matrix_world.translation
    swg_x = float(p.x)
    swg_y = float(p.z)
    swg_z = float(p.y)

    lines = []
    lines.append('\t\tchunk "LOBJ"')
    lines.append("\t\t{")
    lines.append(f"\t\t\t int32 {m_type}")
    lines.append(f'\t\t\tcstring "{appearance}"')
    lines.append(f"\t\t\t float {f6(c1[0])}")
    lines.append(f"\t\t\t float {f6(c1[1])}")
    lines.append(f"\t\t\t float {f6(c1[2])}")
    lines.append(f"\t\t\t float {f6(c2[0])}")
    lines.append(f"\t\t\t float {f6(c2[1])}")
    lines.append(f"\t\t\t float {f6(c2[2])}")
    lines.append(f"\t\t\t float {f6(m_range1)}")
    lines.append(f"\t\t\t float {f6(m_range2)}")
    lines.append(f"\t\t\t float {f6(m_time1)}")
    lines.append(f"\t\t\t float {f6(m_time2)}")
    lines.append(f"\t\t\t float {f6(m_const)}")
    lines.append(f"\t\t\t float {f6(m_lin)}")
    lines.append(f"\t\t\t float {f6(m_quad)}")
    lines.append(f"\t\t\t int32 {stateFlags}")
    lines.append(f"\t\t\t float {f6(swg_x)}")
    lines.append(f"\t\t\t float {f6(swg_y)}")
    lines.append(f"\t\t\t float {f6(swg_z)}")
    lines.append("\t\t}")
    return "\n".join(lines)

def arrow_to_chld(obj):
    """Any object with custom property type='CHLD' -> CHLD block"""
    cstr = str(get_cp(obj, "cstring", ""))

    # Position (Blender -> SWG: swap Y/Z)
    p = obj.matrix_world.translation
    pos_x = float(p.x)
    pos_y = float(p.z)
    pos_z = float(p.y)

    # Orientation
    r = obj.matrix_world.to_euler()
    ori_x = float(degrees(r.x))
    ori_y = float(degrees(r.z))
    ori_z = float(degrees(r.y))

    # motion data
    rps_x = float(get_cp(obj, "rps_x", 0.0))
    rps_y = float(get_cp(obj, "rps_y", 0.0))
    rps_z = float(get_cp(obj, "rps_z", 0.0))
    sps_x = float(get_cp(obj, "sps_x", 0.0))
    sps_y = float(get_cp(obj, "sps_y", 0.0))
    sps_z = float(get_cp(obj, "sps_z", 0.0))
    seesawMag = float(get_cp(obj, "seesawMag", 0.0))
    spring_x = float(get_cp(obj, "spring_x", 0.0))
    spring_y = float(get_cp(obj, "spring_y", 0.0))
    spring_z = float(get_cp(obj, "spring_z", 0.0))
    springsPerSecond = float(get_cp(obj, "springsPerSecond", 0.0))

    lines = []
    lines.append('\t\tchunk "CHLD"')
    lines.append("\t\t{")
    lines.append(f'\t\t\tcstring "{cstr}"')
    lines.append(f"\t\t\t float {f6(pos_x)}")
    lines.append(f"\t\t\t float {f6(pos_y)}")
    lines.append(f"\t\t\t float {f6(pos_z)}")
    lines.append(f"\t\t\t float {f6(ori_x)}")
    lines.append(f"\t\t\t float {f6(ori_y)}")
    lines.append(f"\t\t\t float {f6(ori_z)}")
    lines.append(f"\t\t\t float {f6(rps_x)}")
    lines.append(f"\t\t\t float {f6(rps_y)}")
    lines.append(f"\t\t\t float {f6(rps_z)}")
    lines.append(f"\t\t\t float {f6(sps_x)}")
    lines.append(f"\t\t\t float {f6(sps_y)}")
    lines.append(f"\t\t\t float {f6(sps_z)}")
    lines.append(f"\t\t\t float {f6(seesawMag)}")
    lines.append(f"\t\t\t float {f6(spring_x)}")
    lines.append(f"\t\t\t float {f6(spring_y)}")
    lines.append(f"\t\t\t float {f6(spring_z)}")
    lines.append(f"\t\t\t float {f6(springsPerSecond)}")
    lines.append("\t\t}")
    return "\n".join(lines)

# ------------------------------------------------------------
# collection walking
# ------------------------------------------------------------
def iter_collection_objects(col, recursive=True):
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

def build_cldf_for_collection(col):
    lobjs, chlds = [], []
    print(f"[MIF Export] Scanning '{col.name}'...")
    for o in iter_collection_objects(col, recursive=True):
        if o.type == 'LIGHT' and getattr(o.data, "type", None) == 'POINT':
            lobjs.append(light_to_lobj(o))
        elif str(get_cp(o, "type", "")).upper() == "CHLD":
            chlds.append(arrow_to_chld(o))

    if not lobjs and not chlds:
        return None, 0, 0

    content = []
    content.append('form "CLDF"')
    content.append("{")
    content.append('\tform "0000"')
    content.append("\t{")
    if lobjs:
        content.append("\n".join(lobjs))
    if chlds:
        if lobjs:
            content.append("")  # spacer
        content.append("\n".join(chlds))
    content.append("\t}")
    content.append("}")
    return "\n".join(content), len(lobjs), len(chlds)

# ------------------------------------------------------------
# operator
# ------------------------------------------------------------
class EXPORT_SCENE_OT_collection_mif(bpy.types.Operator):
    """Export active collection POINT lights and CHLDs to clientdata as shared_<collection>.mif"""
    bl_idname = "export_scene.collection_mif"
    bl_label = "Collection to Shared MIF (.mif)"
    filename_ext = ".mif"

    def execute(self, context):
        alc = context.view_layer.active_layer_collection
        if not alc:
            self.report({'ERROR'}, "No active collection selected in the Outliner.")
            return {'CANCELLED'}

        col = alc.collection
        text, n_lobj, n_chld = build_cldf_for_collection(col)
        if not text:
            self.report({'WARNING'}, f'No eligible objects found in "{col.name}".')
            return {'CANCELLED'}

        # build output filename automatically
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = EXPORT_DIR / f"shared_{col.name}.mif"

        out_path.write_text(text, encoding="utf-8")
        self.report({'INFO'}, f'Exported {n_lobj} LOBJ and {n_chld} CHLD from "{col.name}" to "{out_path}"')
        return {'FINISHED'}

# ------------------------------------------------------------
# menu and registration
# ------------------------------------------------------------
def menu_func_export(self, context):
    self.layout.operator(EXPORT_SCENE_OT_collection_mif.bl_idname, text="Collection to Shared MIF (.mif)")

classes = (EXPORT_SCENE_OT_collection_mif,)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
