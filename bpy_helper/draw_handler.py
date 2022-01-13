from abc import ABC, abstractmethod
from typing import Type, Set

from traceback import print_exc

import blf
import bpy

REGISTERED_DRAW_HANDLERS_GLOBAL: Set["AbstractDrawHandler"] = set()


class AbstractDrawHandler(ABC):
    __rna_handle = None

    @property
    @abstractmethod
    def space_type(self) -> Type[bpy.types.Space]:
        pass

    @property
    @abstractmethod
    def region_type(self) -> str:
        pass

    @property
    @abstractmethod
    def draw_type(self) -> str:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

    def init(self) -> None:
        """Method used to initalize data before registering the handler"""
        pass

    def register(self):
        REGISTERED_DRAW_HANDLERS_GLOBAL.add(self)
        self.init()
        # draw must be unbound on Blender >= 3.0.0
        def draw_unbound(draw_handler):
            draw_handler.draw()

        self.__rna_handle = self.space_type.draw_handler_add(draw_unbound, (self,), self.region_type, self.draw_type)

    def unregister(self):
        if self.__rna_handle is None:
            return
        REGISTERED_DRAW_HANDLERS_GLOBAL.discard(self)
        self.space_type.draw_handler_remove(self.__rna_handle, self.region_type)
        self.__rna_handle = None


# Example
class DrawView3DText(AbstractDrawHandler):
    space_type = bpy.types.SpaceView3D
    draw_type = "POST_PIXEL"
    region_type = "WINDOW"

    def init(self, pos_x: float = 100, pos_y: float = 60, line_spacing: float = 5, font_size: float = 20) -> None:
        self.text = ""
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._line_spacing = line_spacing
        self._font_size = font_size

    def set_text(self, text: str) -> None:
        self.text = text

    def set_position(self, x: float, y: float):
        self._pos_x = x
        self._pos_y = y

    def set_line_spacing(self, line_spacing: float):
        self._line_spacing = line_spacing

    def set_font_size(self, font_size: float):
        self._font_size = font_size

    def draw(self) -> None:
        font_id = 0
        font_size = self._font_size
        line_spacing = self._line_spacing
        pos_x = self._pos_x
        pos_y = self._pos_y
        pos_z = 0
        blf.size(font_id, font_size, 72)
        blf.color(font_id, 1.0, 1.0, 1.0, 1.0)

        for line in self.text.splitlines():
            blf.position(font_id, pos_x, pos_y, pos_z)
            blf.draw(font_id, line)
            pos_y -= font_size + line_spacing


def unregister_all_draw_handlers():
    # set must be copied because unregister method modifies the set
    for handler in REGISTERED_DRAW_HANDLERS_GLOBAL.copy():
        try:
            handler.unregister()
        except Exception:
            print_exc()
