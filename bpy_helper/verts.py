from mathutils import Vector, Matrix


def getAverageVert(arrVerts):
    return sum(arrVerts, Vector()) / len(arrVerts)


def getAverageNormal(arrVerts):
    return sum([v.normal for v in arrVerts], Vector()) / len(arrVerts)


def getAverageLocation(arrVerts):
    return sum([v.co for v in arrVerts], Vector()) / len(arrVerts)


def fnTranslateVectors(arrVerts):
    # Translate the vector into a flattened 2d coordinate and save the rotation
    avg_normal = getAverageNormal(arrVerts)
    rot_quat = avg_normal.rotation_difference((0, 0, 1))
    return rot_quat, [(rot_quat @ v.co).to_2d() for v in arrVerts]


def alignObjectToVerts(obj, arrVerts):
    # get the rotation
    rot_quat, arrRotatedVerts = fnTranslateVectors(arrVerts)
    arrVerts = [mathutils.Matrix() @ mathutils.Vector(v.co) for v in arrVerts]
    avgVert = getAverageVert(arrVerts)
    # I like to move it move it
    obj.matrix_world = obj.matrix_world @ Matrix.Translation(avgVert)
    # rotate AFTER move
    obj.rotation_euler.rotate(rot_quat.conjugated())
