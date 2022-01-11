import bpy
import numpy as np


def pca(points: np.ndarray):
    cov_mat = np.cov(points, rowvar=False, bias=True)
    eig_vals, eig_vecs = np.linalg.eigh(cov_mat)

    # ensure right-handed basis
    d = np.sign(np.linalg.det(eig_vecs))
    if d < 0:
        eig_vecs[:, 2] *= -1

    change_of_basis_mat: np.ndarray = eig_vecs
    return change_of_basis_mat


def pca_aligned_span(points: np.ndarray):
    """Returns PCA aligned bounding box dimensions and change of basis matrix"""
    change_of_basis_mat = pca(points)
    inv_change_of_basis_mat = np.linalg.inv(change_of_basis_mat)

    aligned = points.dot(inv_change_of_basis_mat.T)

    bb_min = aligned.min(axis=0)
    bb_max = aligned.max(axis=0)

    span: np.ndarray = bb_max - bb_min
    return span, change_of_basis_mat


def shortest_span_direction(points: np.ndarray):
    """Direction of shortest (PCA oriented) span of points"""
    span, change_of_basis_mat = pca_aligned_span(points)
    shortest_span_dim_index = span.argmin()
    shortest_span_direction = change_of_basis_mat.T[shortest_span_dim_index]

    return shortest_span_direction


def longest_span_direction(points: np.ndarray):
    """Direction of longest (PCA oriented) span of points"""
    span, change_of_basis_mat = pca_aligned_span(points)
    longest_span_dim_index = span.argmax()
    longest_span_direction = change_of_basis_mat.T[longest_span_dim_index]

    return longest_span_direction


def max_face_normal_by_global_z(obj: bpy.types.Object) -> np.ndarray:
    up_vec = obj.matrix_world.col[2]
    faces = obj.data.polygons
    if len(faces) == 0:
        raise RuntimeError(f"{obj} has 0 faces")
    face_normals_arr = np.empty(len(faces) * 3)
    faces.foreach_get("normal", face_normals_arr)
    face_normals_arr.shape = -1, 3
    return face_normals_arr[face_normals_arr.dot(up_vec).argmax()]
