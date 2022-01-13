import importlib
from traceback import print_exc
from typing import List


class ModuleRegisterHelper:
    def __init__(self, parent_module_name: str, module_names: List[str]) -> None:
        self._parent_module_name = parent_module_name
        print(parent_module_name)
        self.modules = [importlib.import_module(f"{parent_module_name}.{name}") for name in module_names]

    def register(self):
        for m in self.modules:
            try:
                m.register()
            except Exception:
                print_exc()

    def unregister(self):
        for m in reversed(self.modules):
            try:
                m.unregister()
            except Exception:
                print_exc()

    def get_register_unregister(self):
        return self.register, self.unregister
