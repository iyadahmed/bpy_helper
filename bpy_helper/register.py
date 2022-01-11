import importlib
import sys
from traceback import print_exc
from typing import List


class ModuleRegisterHelper:
    def __init__(self, module_names: List[str], package: str) -> None:
        self._package = package
        self.modules = [importlib.import_module(name, package) for name in module_names]

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

        for module_name in list(sys.modules.keys()):
            if module_name.startswith(self._package):
                del sys.modules[module_name]
