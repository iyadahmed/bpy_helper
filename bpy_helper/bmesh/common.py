import bpy

import bmesh


def bmesh_to_object(bm: bmesh.types.BMesh, name: str = ""):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    mesh.update()
    obj: bpy.types.Object = bpy.data.objects.new(name, mesh)
    obj.use_fake_user = True
    return obj
