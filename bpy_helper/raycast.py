import bpy
from bpy_extras import view3d_utils
from mathutils import Vector


def ray_cast_visible_objects(context: bpy.types.Context, ray_origin: Vector, ray_target: Vector):
    """Perform ray scene intersection with visible objects

    Args:
        context (bpy.types.Context): Blender Context
        ray_origin (mathutils.Vector): Ray origin in world coordinates
        ray_target (mathutils.Vector): Ray target in world coordinates

    Returns:
        normal (mathutils.Vector),
        location (mathutils.Vector),
        obj (bpy.types.Object),
        polygon_index (int)
    """
    if context.mode == "EDIT_MESH":
        print("WARNING: ray cast in edit mode, some objects might not be visible to ray cast")

    ray_direction = Vector(ray_target - ray_origin).normalized()
    depsgraph = context.evaluated_depsgraph_get()
    is_hit, location, normal, index, obj, matrix = context.scene.ray_cast(depsgraph, ray_origin, ray_direction)
    if is_hit:
        return normal, location, obj, index

    return None, None, None, None


def region_to_ray(context: bpy.types.Context, x, y):
    """Returns ray origin and ray target in world coordinates from a poistion in a 2D region"""
    region = context.region
    rv3d = context.region_data
    coord = x, y

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    ray_target: Vector = ray_origin + view_vector

    return ray_origin, ray_target
