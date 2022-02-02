from typing import Iterable

import numpy as np
from mathutils import Matrix, Vector


def det_2x2(mat) -> float:
    return mat[0] * mat[3] - mat[1] * mat[2]


def line_line_intersection_2d_params(v1, v2, v3, v4, epsilon=0.000001):
    x1, y1 = v1
    x2, y2 = v2
    x3, y3 = v3
    x4, y4 = v4
    t1 = det_2x2((x1 - x3, x3 - x4, y1 - y3, y3 - y4))
    t2 = det_2x2((x1 - x2, x3 - x4, y1 - y2, y3 - y4))
    if abs(t2) < epsilon:
        return None, None

    u1 = det_2x2((x1 - x3, x1 - x2, y1 - y3, y1 - y2))
    u2 = det_2x2((x1 - x2, x3 - x4, y1 - y2, y3 - y4))
    if abs(u2) < epsilon:
        return None, None

    return t1 / t2, u1 / u2


def line_line_intersection_2d(v1, v2, v3, v4, epsilon=0.000001):
    x1, y1 = v1
    x2, y2 = v2
    x3, y3 = v3
    x4, y4 = v4
    t1 = det_2x2((x1 - x3, x3 - x4, y1 - y3, y3 - y4))
    t2 = det_2x2((x1 - x2, x3 - x4, y1 - y2, y3 - y4))
    if abs(t2) < epsilon:
        return None, None

    t = t1 / t2

    return t * (x2 - x1), t * (y2 - y1)


def transform_normal_np(mat_3x3: np.ndarray, vec3: np.ndarray):
    return vec3.dot(np.linalg.inv(mat_3x3))  # reduced from inv(mat).T.T


def transform_normal(mat: Matrix, vec: Vector) -> Vector:
    return mat.inverted_safe().transposed() @ vec


def vector_mean(vectors: Iterable[Vector]):
    return sum(vectors, Vector())
