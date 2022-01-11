import bpy

import bmesh


def fatten_even(mesh: bpy.types.Mesh, distance: float = 1.0):
    bm = bmesh.new(use_operators=False)
    bm.from_mesh(mesh)
    v: bmesh.types.BMVert
    for v in bm.verts:
        v.co += v.normal * v.calc_shell_factor() * distance

    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
