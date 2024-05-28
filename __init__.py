bl_info = {
    "name": "Quick Animation Exporter",
    "description": "Quickly choose animations to export for selected rig",
    "author": "Samjooma",
    "version": (1, 0, 0),
    "blender": (4, 1, 0),
    "category": "Import-Export"
}

import bpy
from . import export_operator

def register():
    export_operator.register()

def unregister():
    export_operator.unregister()

if __name__ == "__main__":
    register()