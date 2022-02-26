from typing import Iterable, Union

import bpy
from bpy.types import MeshVertex, Object
from mathutils import Matrix, Vector

import bmesh
from bmesh.types import BMVert

from .math import vector_mean


def shade_flat(mesh: bpy.types.Mesh):
    num_poly = len(mesh.polygons)
    mesh.polygons.foreach_set("use_smooth", (False,) * num_poly)
    mesh.update()


def fatten_even(mesh: bpy.types.Mesh, distance: float = 1.0):
    bm = bmesh.new(use_operators=False)
    bm.from_mesh(mesh)
    v: bmesh.types.BMVert
    for v in bm.verts:
        v.co += v.normal * v.calc_shell_factor() * distance

    bm.to_mesh(mesh)
    mesh.update()
    bm.free()


def calc_mean_verts_normal(verts: Iterable[Union[MeshVertex, BMVert]]):
    return sum((v.normal / len(verts) for v in verts), Vector())


def calc_mean_verts_co(verts: Iterable[Union[MeshVertex, BMVert]]):
    return sum((v.co / len(verts) for v in verts), Vector())


def get_verts_flattened(verts: Iterable[Union[MeshVertex, BMVert]]):
    """Rotate vertices to be aligned with their mean normal, and flatten the to XY plane,
    returns the Quaternion used for rotation and the flattened 2D vertices"""
    avg_normal = calc_mean_verts_normal(verts)
    rot_quat = avg_normal.rotation_difference((0, 0, 1))
    return rot_quat, [(rot_quat @ v.co).to_2d() for v in verts]


def align_object_to_verts(obj: Object, verts: Iterable[Union[MeshVertex, BMVert]]):
    """Align an object to a plane with mean of vertex normals and goes through mean of vertex locations"""
    # get the rotation
    rot_quat, _ = get_verts_flattened(verts)
    avg_co = vector_mean(v.co for v in verts)
    # I like to move it move it
    obj.matrix_world = obj.matrix_world @ Matrix.Translation(avg_co)
    # rotate AFTER move
    obj.rotation_euler.rotate(rot_quat.conjugated())
