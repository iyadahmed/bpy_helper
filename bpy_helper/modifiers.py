import bpy
from typing import List


def apply_modifiers(
    context: bpy.types.Context,
    obj: bpy.types.Object,
    target_mods: List[bpy.types.Modifier],
):
    for mod in target_mods:
        assert mod.id_data == obj

    viewport_visibility_original = dict()
    mod: bpy.types.Modifier
    for mod in obj.modifiers:
        viewport_visibility_original[mod] = mod.show_viewport
        mod.show_viewport = False

    for mod in target_mods:
        mod.show_viewport = True

    dg = context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))

    for mod in target_mods:
        obj.modifiers.remove(mod)

    obj.data = mesh

    for mod in obj.modifiers:
        mod.show_viewport = viewport_visibility_original[mod]


def apply_modifier_by_name(obj: bpy.types.Object, modifier_name: str):
    apply_modifiers(bpy.context, obj, [obj.modifiers[modifier_name]])


def apply_modifier(
    context: bpy.types.Context, obj: bpy.types.Object, modifier: bpy.types.Modifier
):
    apply_modifiers(context, obj, [modifier])


def create_boolean_modifier_obj_obj_fast(obj_first, obj_second, operation):
    mod: bpy.types.BooleanModifier = obj_first.modifiers.new("", "BOOLEAN")
    mod.solver = "FAST"
    mod.operation = operation
    mod.object = obj_second
    return mod


def create_boolean_modifier_obj_obj_exact(
    obj_first, obj_second, operation, use_hole_tolerant=False, use_self=False
):
    mod: bpy.types.BooleanModifier = obj_first.modifiers.new("", "BOOLEAN")
    mod.solver = "EXACT"
    mod.operation = operation
    mod.use_hole_tolerant = use_hole_tolerant
    mod.use_self = use_self
    mod.object = obj_second
    return mod


def create_remesh_modifier_sharp(obj: bpy.types.Object, octree_depth=6):
    mod: bpy.types.RemeshModifier = obj.modifiers.new("", "REMESH")
    mod.mode = "SHARP"
    mod.octree_depth = octree_depth
    mod.use_remove_disconnected = False
    return mod


def create_remesh_modifier_voxel(obj: bpy.types.Object, voxel_size=0.35):
    mod: bpy.types.RemeshModifier = obj.modifiers.new("", "REMESH")
    mod.mode = "VOXEL"
    mod.voxel_size = voxel_size
    return mod


def create_triangulate_modifier(obj: bpy.types.Object):
    mod: bpy.types.TriangulateModifier = obj.modifiers.new("", "TRIANGULATE")
    mod.quad_method = "BEAUTY"
    mod.ngon_method = "BEAUTY"
    return mod


def create_solidify_modifier_rim_only(obj: bpy.types.Object, thickness=0.1):
    mod: bpy.types.SolidifyModifier = obj.modifiers.new("", "SOLIDIFY")
    mod.use_rim_only = True
    mod.thickness = thickness
    return mod


def create_geometry_nodes_modifier(
    obj: bpy.types.Object,
    name: str = "",
    node_tree: bpy.types.GeometryNodeTree | None = None,
):
    mod: bpy.types.GeometryNodesModifier = obj.modifiers.new(name, "GEOMETRY_NODES")
    if node_tree:
        mod.node_group = node_tree
    return mod
