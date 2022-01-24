import bpy
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

import bmesh
from bmesh.types import BMesh, BMVert, BMEdge


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
    rot_mat_inv = rot_mat.inverted_safe()

    (
        delauny_verts_co,
        delauny_edges,
        delauny_faces,
        delauny_orig_verts,
        delauny_orig_edges,
        delauny_orig_faces,
    ) = delaunay_2d_cdt(
        [(rot_mat_inv @ project_point_to_plane(v.co, plane_co, plane_normal))[:2] for v in delauny_verts_input],
        delauny_edges_input,
        [],
        1,
        0.00001,
    )

    delauny_verts_bm_out = [
        bm.verts.new(project_point_to_plane(co.to_3d(), plane_co, plane_normal)) for co in delauny_verts_co
    ]

    for df in delauny_faces:
        v0 = delauny_verts_bm_out[df[0]]
        v1 = delauny_verts_bm_out[df[1]]
        v2 = delauny_verts_bm_out[df[2]]
        bm.faces.new((v0, v1, v2))


if __name__ == "__main__":
    edit_mesh = bpy.context.object.data
    bm = bmesh.from_edit_mesh(edit_mesh)
    bisect_fill(bm, Vector((0, 0, 21)), Vector((0, 0, 1)))
    bmesh.update_edit_mesh(edit_mesh)
