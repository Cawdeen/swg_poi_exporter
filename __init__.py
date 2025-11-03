bl_info = {
    "name": "SWG POI Exporter",
    "author": "Collin Farrell",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "File > Export",
    "description": "Exports SWG MIF and POI data from Blender collections",
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    importlib.reload(mif_exporter)
    importlib.reload(poi_exporter)
    importlib.reload(poi_template_generator)
else:
    from . import mif_exporter
    from . import poi_exporter
    from . import poi_template_generator

import bpy

def register():
    mif_exporter.register()
    poi_exporter.register()
    poi_template_generator.register()

def unregister():
    poi_template_generator.unregister()
    poi_exporter.unregister()
    mif_exporter.unregister()

if __name__ == "__main__":
    register()

