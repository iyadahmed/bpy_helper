from dataclasses import dataclass

import bpy
from bpy_extras import view3d_utils
from mathutils import Matrix, Vector


@dataclass(frozen=True)
class RayHit:
    is_hit: bool
    location: Vector
    normal: Vector
    polygon_index: int
    obj: bpy.types.Object
    obj_matrix: Matrix

    def __bool__(self):
        return self.is_hit


def ray_cast_scene(context: bpy.types.Context, ray_origin, ray_direction):
    dg = context.evaluated_depsgraph_get()
    is_hit, location, normal, polygon_index, obj, obj_matrix = context.scene.ray_cast(dg, ray_origin, ray_direction)
    return RayHit(is_hit, location, normal, polygon_index, obj, obj_matrix)


def region_2d_to_ray_view3d(context: bpy.types.Context, x: int, y: int):
    """Returns a tuple (ray_origin, ray_direction) in world space"""
    region = context.region
    region_view_3d = context.region_data
    coord = x, y

    ray_direction = view3d_utils.region_2d_to_vector_3d(region, region_view_3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_view_3d, coord)
    return ray_origin, ray_direction
