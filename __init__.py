bl_info = {
    "name": "Quick Action Export",
    "description": "Quickly export actions to FBX files",
    "author": "Samjooma",
    "version": (1, 0, 0),
    "blender": (4, 1, 0),
    "category": "Import-Export"
}

import bpy
from . import export_actions_operator

def register():
    export_actions_operator.register()

def unregister():
    export_actions_operator.unregister()

if __name__ == "__main__":
    register()