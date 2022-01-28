from dataclasses import dataclass
from math import trunc

import bpy


@dataclass
class Rect:
    xmin: float = 0
    xmax: float = 0
    ymin: float = 0
    ymax: float = 0

    def size_x(self):
        return self.xmax - self.xmin

    def size_y(self):
        return self.ymax - self.ymin

    def scale_x(self, origin: float, factor: float):
        self.xmin -= origin
        self.xmax -= origin

        self.xmin *= factor
        self.xmax *= factor

        self.xmin += origin
        self.xmax += origin

    def scale_y(self, origin: float, factor: float):
        self.ymin -= origin
        self.ymax -= origin

        self.ymin *= factor
        self.ymax *= factor

        self.ymin += origin
        self.ymax += origin


def view_to_region_rect(rect: Rect, view2d: bpy.types.View2D, clip: bool = False):
    new_rect = Rect()
    new_rect.xmin, new_rect.ymin = view2d.view_to_region(
        rect.xmin, rect.ymin, clip=clip
    )
    new_rect.xmax, new_rect.ymax = view2d.view_to_region(
        rect.xmax, rect.ymax, clip=clip
    )
    return new_rect


def abs_node_location(node):
    abs_location = node.location
    if node.parent is None:
        return abs_location
    return abs_location + abs_node_location(node.parent)


def node_to_view(node):
    sys_prefs = bpy.context.preferences.system
    dpi_fac = sys_prefs.ui_scale
    x, y = abs_node_location(node)
    return x * dpi_fac, y * dpi_fac


# https://github.com/blender/blender/blob/035dcdad90ec9d6881e2d99b90e30f5a481237e1/source/blender/windowmanager/intern/wm_window.c#L513
def get_widget_unit():
    sys_prefs = bpy.context.preferences.system
    pixelsize = sys_prefs.pixel_size
    dpi = sys_prefs.dpi
    dpi_fac = sys_prefs.ui_scale
    widget_unit = (pixelsize * dpi * 20 + 36) / 72
    widget_unit += 2 * (trunc(pixelsize) - trunc(dpi_fac))
    return widget_unit


def NODE_WIDTH(node):
    sys_prefs = bpy.context.preferences.system
    dpi_fac = sys_prefs.ui_scale
    return node.width * dpi_fac
