import importlib
import sys

from traceback import print_exc


class ModuleRegisterHelper:
    def __init__(self, parent_module_name, module_names) -> None:
        self.full_module_names = [f"{parent_module_name}.{name}" for name in module_names]
        for name in self.full_module_names:
            importlib.import_module(name)

    def register(self):
        for name in self.full_module_names:
            try:
                sys.modules[name].register()
            except Exception:
                print_exc()

    def unregister(self):
        for name in reversed(self.full_module_names):
            try:
                sys.modules[name].unregister()
            except Exception:
                print_exc()
