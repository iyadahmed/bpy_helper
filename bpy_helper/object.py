from typing import List

import bpy
from mathutils import Matrix, Vector

import bmesh

from .bmesh.loose_parts import bm_loose_parts


def obj_mesh_copy(obj: bpy.types.Object):
    assert obj.type == "MESH"
    new_obj = obj.copy()
    new_obj.data = bpy.data.meshes.new_from_object(obj)
    new_obj.use_fake_user = True
    return new_obj


def obj_get_loose_parts(obj: bpy.types.Object):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    loose_parts = [region.to_obj(obj.name) for region in bm_loose_parts(bm)]
    bm.free()
    return loose_parts


def obj_join_mesh_objects(objs: List[bpy.types.Object]):
    bm = bmesh.new(use_operators=False)

    for obj in objs:
        if obj.type != "MESH":
            bm.free()
            raise RuntimeError("Only mesh objects can be joined together")
        bm.from_mesh(obj.data)

    joined_mesh = bpy.data.meshes.new("Joined Mesh Object")
    joined_obj = bpy.data.objects.new(joined_mesh.name, joined_mesh)
    joined_obj.use_fake_user = True
    bm.to_mesh(joined_mesh)
    joined_mesh.update()
    bm.free()

    return joined_obj


# workaround annoying issue where sometimes view3d poll fails
def view_selected_all_regions(context: bpy.types.Context):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for region in area.regions:
                if region.type != "WINDOW":
                    continue
                bpy.ops.view3d.view_selected({"region": region, "area": area})


def focus_viewport(context: bpy.types.Context, target_objs: List[bpy.types.Object]):
    """Hide all other objects, show the targets and focus viewport on them"""
    obj: bpy.types.Object
    for obj in context.view_layer.objects:
        obj.hide_set(True, view_layer=context.view_layer)

    for obj in target_objs:
        obj.hide_set(False, view_layer=context.view_layer)
        obj.select_set(True, view_layer=context.view_layer)

    view_selected_all_regions(context)


def ensure_object_mode(context: bpy.types.Context):
    ctx = context.copy()
    if bpy.ops.object.mode_set.poll(ctx):
        bpy.ops.object.mode_set(ctx, mode="OBJECT")

    if context.mode != "OBJECT":
        raise RuntimeError("Failed to ensure Object mode")


def select_object(context: bpy.types.Context, obj: bpy.types.Object):
    if obj is None:
        return
    # objects cannot be selected if they are not linked to a collection in the active view layer
    if obj.name not in context.view_layer.objects:
        context.scene.collection.objects.link(obj)
    obj.hide_set(False)  # objects cannot be selected if they are hidden
    obj.select_set(True)


def activate_object(context: bpy.types.Context, obj: bpy.types.Object):
    select_object(context, obj)  # objects cannot be active if they are not selected
    context.view_layer.objects.active = obj


def set_origin(obj: bpy.types.Object, location: Vector):
    me = obj.data
    mw = obj.matrix_world
    me.transform(Matrix.Translation(-location))
    mw.translation = mw @ location


def get_center_bounds(obj: bpy.types.Object, axis="z", dir="-"):
    """Get bounding box center snapped to face pointing to a positive or negative axis"""
    bb_center = sum((v.co / 8 for v in obj.bound_box), Vector())
    if dir == "-":
        bb_center[axis] = min(v.co[axis] for v in obj.bound_box)
    else:
        bb_center[axis] = max(v.co[axis] for v in obj.bound_box)
    return bb_center


def obj_copy_translation(obj_from: bpy.types.Object, obj_to: bpy.types.Object):
    obj_to.matrix_world.translation = obj_from.matrix_world.translation.copy()


def obj_remove_small_parts(obj: bpy.types.Object):
    assert obj.type == "MESH"
    bm = bmesh.new(use_operators=False)
    mesh: bpy.types.Mesh = obj.data
    bm.from_mesh(mesh)
    loose_parts = bm_loose_parts(bm)
    for lp in loose_parts:
        lp.update_bounding_box()
    for lp in sorted(loose_parts, key=lambda lp: (lp.bb_max - lp.bb_min).length_squared)[:-1]:
        for v in lp.verts:
            bm.verts.remove(v)
    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
