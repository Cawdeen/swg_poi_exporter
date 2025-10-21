bl_info = {
    "name": "SWG Export Tools",
    "author": "Collin Farrell",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "File > Export",
    "description": "Combined tools for SWG exports (.mif and .txt table)",
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    importlib.reload(mif_exporter)
    importlib.reload(poi_exporter)
else:
    from . import mif_exporter
    from . import poi_exporter

import bpy

def register():
    mif_exporter.register()
    poi_exporter.register()

def unregister():
    poi_exporter.unregister()
    mif_exporter.unregister()

if __name__ == "__main__":
    register()
