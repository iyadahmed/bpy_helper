import importlib
import sys
from traceback import print_exc
from typing import List


# Based on https://devtalk.blender.org/t/plugin-hot-reload-by-cleaning-sys-modules/20040
def cleanse_modules(parent_module_name):
    """search for your plugin modules in blender python sys.modules and remove them"""

    for module_name in list(sys.modules.keys()):
        if module_name.startswith(parent_module_name):
            del sys.modules[module_name]


# Similar to bpy.utils.register_submodule_factory
def module_register_factory(parent_module_name: str, module_names: List[str]):
    modules = [importlib.import_module(f"{parent_module_name}.{name}") for name in module_names]

    def register():
        for m in modules:
            try:
                m.register()
            except Exception:
                print_exc()

    def unregister():
        for m in reversed(modules):
            try:
                m.unregister()
            except Exception:
                print_exc()

    return register, unregister
