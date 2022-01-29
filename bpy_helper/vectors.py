import bpy, bmesh, mathutils

def vector_flatten(arrVerts):
    # get 2d points for 3d vectors
    avg_normal = mathutils.Vector()
    for v in arrVerts:
        avg_normal += (v.normal / len(arrVerts))
    rot_quat = avg_normal.rotation_difference((0, 0, 1))
    return [(rot_quat @ v.co).to_2d() for v in arrVerts]