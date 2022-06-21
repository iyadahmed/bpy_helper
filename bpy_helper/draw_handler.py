from abc import ABC, abstractmethod
from copy import deepcopy
from traceback import print_exc
from typing import Set, Type, Tuple, List, Union

import blf
import bgl
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d as vec_3d_2d

REGISTERED_DRAW_HANDLERS_GLOBAL: Set["AbstractDrawHandler"] = set()

int_or_float = Union[int, float]
color4 = Tuple[int_or_float, int_or_float, int_or_float, int_or_float]
pos3 = Union[
    Tuple[Tuple[int_or_float, int_or_float, int_or_float], ...],
    List[Tuple[int_or_float, int_or_float, int_or_float]],
]

_t2_3 = Union[Tuple[int_or_float, int_or_float], Tuple[int_or_float, int_or_float]]
indices = Union[Tuple[_t2_3, ...], List[Tuple[_t2_3]]]


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

        self.__rna_handle = self.space_type.draw_handler_add(
            draw_unbound, (self,), self.region_type, self.draw_type
        )

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

    def init(
        self,
        pos_x: float = 100,
        pos_y: float = 60,
        line_spacing: float = 5,
        font_size: float = 20,
        color: color4 = (1.0, 1.0, 1.0, 1.0),
    ) -> None:

        self.text = ""
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._line_spacing = line_spacing
        self._font_size = font_size
        self._color = color

    def set_text(self, text: str) -> None:
        self.text = text

    def set_position(self, x: float, y: float):
        self._pos_x = x
        self._pos_y = y

    def set_color(self, color: color4):
        self._color = deepcopy(color)

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
        blf.color(font_id, *self._color)

        for line in self.text.splitlines():
            blf.position(font_id, pos_x, pos_y, pos_z)
            blf.draw(font_id, line)
            pos_y -= font_size + line_spacing


class DrawGeometry3D(AbstractDrawHandler):
    space_type = bpy.types.SpaceView3D
    draw_type = "POST_VIEW"
    region_type = "WINDOW"

    def init(self) -> None:
        self.verts: pos3 = []
        self.tris_vert_indices: indices = []
        self.color: color4 = (0.0, 0.0, 1.0, 0.75)

    def set_geometry(self, verts: pos3, triangles):
        self.verts = deepcopy(verts)
        self.tris_vert_indices = deepcopy(triangles)

    def set_color(self, color: color4):
        self.color = deepcopy(color)

    def draw(self) -> None:
        shader: gpu.types.GPUShader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
        batch: gpu.types.GPUBatch = batch_for_shader(
            shader,
            "TRIS",
            {"pos": self.verts},
            indices=self.tris_vert_indices,
        )
        shader.bind()
        shader.uniform_float("color", self.color)
        gpu.state.blend_set("ALPHA")
        batch.draw(shader)
        gpu.state.blend_set("NONE")


class DrawPoints3D(AbstractDrawHandler):
    space_type = bpy.types.SpaceView3D
    draw_type = "POST_VIEW"
    region_type = "WINDOW"

    def init(self) -> None:
        self.points: pos3 = []
        self.point_size: float = 5
        self.color: Union[List[color4], Tuple[color4, ...]] = [(1.0, 1.0, 1.0, 1.0)]

    def set_points(self, verts: pos3):
        self.points = deepcopy(verts)

    def set_color(self, color: Union[List[color4], Tuple[color4, ...]]):
        self.color = deepcopy(color)

    def set_size(self, size):
        self.point_size = deepcopy(size)

    def draw(self) -> None:
        shader: gpu.types.GPUShader = gpu.shader.from_builtin("3D_FLAT_COLOR")
        batch: gpu.types.GPUBatch = batch_for_shader(
            shader,
            "POINTS",
            {
                "pos": self.points,
                "color": self.color,
            },
        )

        bgl.glPointSize(self.point_size)
        bgl.glEnable(bgl.GL_DEPTH_TEST)
        shader.bind()
        gpu.state.blend_set("ALPHA")
        batch.draw(shader)
        gpu.state.blend_set("NONE")


# TODO: needs a better name
class DrawView2D3DText(AbstractDrawHandler):
    space_type = bpy.types.SpaceView3D
    draw_type = "POST_PIXEL"
    region_type = "WINDOW"

    def init(
        self,
        pos_x: float = 0,
        pos_y: float = 0,
        pos_z: float = 1,
        font_size: float = 20,
    ) -> None:
        self.text = ""
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._pos_z = pos_z
        self._font_size = font_size
        self.color: color4 = (1.0, 1.0, 1.0, 1.0)

    def set_text(self, text: str) -> None:
        self.text = text

    def set_color(self, color: color4):
        self.color = deepcopy(color)

    def set_position(self, x: float, y: float, z: float):
        self._pos_x = x
        self._pos_y = y
        self._pos_z = z

    def set_font_size(self, font_size: float):
        self._font_size = font_size

    def draw(self) -> None:
        pos_y = self._pos_y
        font_id = 0
        v3d = bpy.context.space_data
        rv3d = v3d.region_3d
        region = bpy.context.region

        vec = vec_3d_2d(region, rv3d, (self._pos_x, self._pos_y, self._pos_z))

        blf.position(font_id, vec[0], vec[1], 0)
        blf.size(font_id, self._font_size, 72)
        blf.draw(font_id, self.text)
        blf.color(font_id, *self.color)


def unregister_all_draw_handlers():
    # set must be copied because unregister method modifies the set
    for handler in REGISTERED_DRAW_HANDLERS_GLOBAL.copy():
        try:
            handler.unregister()
        except Exception:
            print_exc()
