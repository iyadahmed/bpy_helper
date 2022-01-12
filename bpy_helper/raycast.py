import bpy
from bpy_extras import view3d_utils


def region_2d_to_ray_view3d(context: bpy.types.Context, x: int, y: int):
    """Returns a tuple (ray_origin, ray_direction) in world space"""
    region = context.region
    region_view_3d = context.region_data
    coord = x, y

    ray_direction = view3d_utils.region_2d_to_vector_3d(region, region_view_3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_view_3d, coord)
    return ray_origin, ray_direction
