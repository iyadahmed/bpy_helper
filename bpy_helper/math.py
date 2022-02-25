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
    return sum((co / len(vectors) for co in vectors), Vector())


def sample_tri(a: Vector, b: Vector, c: Vector, u: float, v: float):
    """Sample a point inside triangle using two values u and v in range [0., 1.]"""
    if (u + v) > 1:
        u = 1 - u
        v = 1 - v
    return c + u * (a - c) + v * (b - c)


def circumcircle(a, b, c):
    """Calculates center of circle going through 3 points a, b, c"""

    # https://math.stackexchange.com/a/1743505/691043
    u1 = b - a
    w1 = c - a

    # Unit vectors for plane containing the three points
    u = u1.normalized()
    w = w1.cross(u1).normalized()
    v = w.cross(u)

    # Project points into the plane
    x_x = u1.dot(u)
    y_x = w1.dot(u)
    y_y = w1.dot(v)

    h = (y_x - x_x / 2) ** 2 + y_y**2 - (x_x / 2) ** 2
    if abs(y_y) < 0.00001:
        return None

    h /= 2 * y_y

    return a + (x_x / 2) * u + h * v
