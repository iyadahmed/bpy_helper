import bpy
from mathutils import Vector
from mathutils.geometry import area_tri, delaunay_2d_cdt
from numpy.random import default_rng

import bmesh
from bmesh.types import BMEdge, BMesh, BMVert

RNG = default_rng(12345)


def sample_tri(a, b, c, u, v):
    u = float(u)
    v = float(v)
    if (u + v) > 1:
        u = 1 - u
        v = 1 - v
    return c + u * (a - c) + v * (b - c)


def sample_tri_randn(a, b, c, n):
    for u, v in RNG.random((n, 2)):
        yield sample_tri(a, b, c, u, v)


def sample_tri_rand_desnity(a, b, c, density):
    """Density in points per area unit"""
    n = int(density * area_tri(a, b, c))
    yield from sample_tri_randn(a, b, c, n)


def project_point_to_plane(point_co, plane_co, plane_normal):
    return point_co - (point_co - plane_co).dot(plane_normal) * plane_normal


def bisect_fill(bm: BMesh, plane_co: Vector, plane_normal: Vector):
    plane_co = Vector(plane_co)
    plane_normal = Vector(plane_normal)
    geom_cut = bmesh.ops.bisect_plane(
        bm,
        geom=bm.faces[:] + bm.edges[:] + bm.verts[:],
        dist=0.0001,
        plane_co=plane_co,
        plane_no=plane_normal,
        use_snap_center=False,
        clear_outer=True,
        clear_inner=False,
    ).get("geom_cut", None)

    if geom_cut is None:
        return

    delauny_verts_input_index_map = dict()
    delauny_verts_input = []

    for v in filter(lambda elem: isinstance(elem, BMVert), geom_cut):
        delauny_verts_input_index_map[v] = len(delauny_verts_input)
        delauny_verts_input.append(v)

    delauny_edges_input = []

    for e in filter(lambda elem: isinstance(elem, BMEdge), geom_cut):
        v0_index = delauny_verts_input_index_map[e.verts[0]]
        v1_index = delauny_verts_input_index_map[e.verts[1]]
        delauny_edges_input.append((v0_index, v1_index))

    rot_mat = plane_normal.rotation_difference((0, 0, 1)).to_matrix()
    rot_mat_t = rot_mat.transposed()
    rot_mat_inv = rot_mat.inverted_safe()
    rot_mat_inv_t = rot_mat_inv.transposed()

    delauny_input_verts_co = [
        (rot_mat_inv_t @ project_point_to_plane(v.co, plane_co, plane_normal))[:2] for v in delauny_verts_input
    ]

    (
        delauny_verts_co,
        delauny_edges,
        delauny_faces,
        delauny_orig_verts,
        delauny_orig_edges,
        delauny_orig_faces,
    ) = delaunay_2d_cdt(
        delauny_input_verts_co,
        delauny_edges_input,
        [],
        1,
        0.00001,
    )

    extra_delauny_input_points = []
    for df in delauny_faces:
        v0 = delauny_verts_co[df[0]].to_3d()
        v1 = delauny_verts_co[df[1]].to_3d()
        v2 = delauny_verts_co[df[2]].to_3d()
        extra_delauny_input_points.extend(co.to_2d() for co in sample_tri_rand_desnity(v0, v1, v2, 10))

    (
        delauny_verts_co,
        delauny_edges,
        delauny_faces,
        delauny_orig_verts,
        delauny_orig_edges,
        delauny_orig_faces,
    ) = delaunay_2d_cdt(
        delauny_input_verts_co + extra_delauny_input_points,
        delauny_edges_input,
        [],
        1,
        0.00001,
    )

    delauny_verts_bm_out = [
        bm.verts.new(project_point_to_plane(rot_mat_t @ co.to_3d(), plane_co, plane_normal)) for co in delauny_verts_co
    ]

    for df in delauny_faces:
        v0 = delauny_verts_bm_out[df[0]]
        v1 = delauny_verts_bm_out[df[1]]
        v2 = delauny_verts_bm_out[df[2]]
        bm.faces.new((v0, v1, v2))

    verts_to_be_smoothed = []
    boundary_verts = []
    for v in delauny_verts_bm_out:
        if next((e for e in v.link_edges if e.is_boundary), None) is None:
            verts_to_be_smoothed.append(v)
        else:
            boundary_verts.append(v)

    for _ in range(10):
        bmesh.ops.smooth_vert(
            bm, verts=verts_to_be_smoothed, factor=1, use_axis_x=True, use_axis_y=True, use_axis_z=True
        )

    bmesh.ops.remove_doubles(bm, verts=delauny_verts_input + boundary_verts, dist=0.0001)


if __name__ == "__main__":
    edit_mesh = bpy.context.object.data
    bm = bmesh.from_edit_mesh(edit_mesh)
    bisect_fill(bm, Vector((0, 0, 21)), Vector((0, 0, 1)))
    bmesh.update_edit_mesh(edit_mesh)
