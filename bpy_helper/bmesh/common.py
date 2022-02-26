import bpy
from mathutils import Matrix

import bmesh


def bmesh_to_object(bm: bmesh.types.BMesh, name: str = ""):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    mesh.update()
    obj: bpy.types.Object = bpy.data.objects.new(name, mesh)
    obj.use_fake_user = True
    return obj


def create_cylinder(bm: bmesh.types.BMesh, radius: float, height: float, mat: Matrix, calc_uvs: bool = False):
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=True,
        segments=64,
        **(
            {"diameter1": radius, "diameter2": radius}
            if bpy.app.version < (3, 0, 0)
            else {"radius1": radius, "radius2": radius}
        ),
        depth=height,
        matrix=mat,
        calc_uvs=calc_uvs,
    )
