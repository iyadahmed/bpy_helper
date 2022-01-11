import bpy


def apply_modifier_by_name(obj: bpy.types.Object, modifier_name: str):
    bpy.ops.object.modifier_apply({"object": obj}, modifier=modifier_name)


def create_boolean_modifier_obj_obj_fast(obj_first, obj_second, operation):
    mod: bpy.types.BooleanModifier = obj_first.modifiers.new("", "BOOLEAN")
    mod.solver = "FAST"
    mod.operation = operation
    mod.object = obj_second
    return mod


def create_boolean_modifier_obj_obj_exact(obj_first, obj_second, operation, use_hole_tolerant, use_self):
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
