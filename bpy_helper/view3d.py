from bpy.types import RegionView3D, Region
from mathutils import Vector

# Functions based on C equivalent in Blender source
def view3d_calc_zfac(rv3d: RegionView3D, co: Vector):
    mat = rv3d.perspective_matrix
    zfac = (mat[0][3] * co[0]) + (mat[1][3] * co[1]) + (mat[2][3] * co[2]) + mat[3][3]
    r_flip = zfac < 0.0

    # if x,y,z is exactly the viewport offset, zfac is 0 and we don't want that
    # (accounting for near zero values)
    if zfac < 1.0e-6 and zfac > -1.0e-6:
        zfac = 1.0

    # Negative zfac means x, y, z was behind the camera (in perspective).
    # This gives flipped directions, so revert back to ok default case.
    if zfac < 0.0:
        zfac = -zfac

    return zfac, r_flip


def view3d_win_to_delta(region: Region, vec_2d: Vector, zfac: float):
    rv3d: RegionView3D = region.data
    dx = 2.0 * vec_2d[0] * zfac / region.width
    dy = 2.0 * vec_2d[1] * zfac / region.width

    persinv = rv3d.perspective_matrix.inverted_safe()

    out = Vector()
    out[0] = persinv[0][0] * dx + persinv[1][0] * dy
    out[1] = persinv[0][1] * dx + persinv[1][1] * dy
    out[2] = persinv[0][2] * dx + persinv[1][2] * dy
    return out
