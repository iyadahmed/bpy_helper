from dataclasses import dataclass
from typing import Iterable

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

from ..bmesh.bmesh import bmesh_to_object


@dataclass
class Cylinder:
    radius: float
    depth: float
    center: Iterable[float]
    up: Iterable[float]

    def calc_volume(self):
        return np.pi * self.radius * self.radius * self.depth

    def to_object(self, mat: Matrix):
        mat = mat @ Vector(self.up).rotation_difference((0, 0, 1))
        mat.translation = self.center
        bm = bmesh.new(use_operators=True)
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            cap_tris=True,
            segments=64,
            **(
                {"diameter1": self.radius, "diameter2": self.radius}
                if bpy.app.version < (3, 0, 0)
                else {"radius1": self.radius, "radius2": self.radius}
            ),
            depth=self.depth,
            matrix=mat,
            calc_uvs=False,
        )
        obj = bmesh_to_object(bm, "")
        bm.free()
        return obj


def pca_mat(points: np.ndarray):
    cov_mat = np.cov(points, rowvar=False, bias=True)
    eig_vals, eig_vecs = np.linalg.eigh(cov_mat)

    # ensure right-handed basis
    d = np.sign(np.linalg.det(eig_vecs))
    if d < 0:
        eig_vecs[:, 2] *= -1

    return eig_vecs


def pseudo_minimum_bounding_cylinder(obj):
    obj = bpy.context.object
    verts = obj.data.vertices
    verts_co = np.empty(len(verts) * 3)
    verts.foreach_get("co", verts_co)
    verts_co.shape = -1, 3

    verts_co_homogenus = np.c_[verts_co, np.ones(len(verts))]
    verts_co_world = verts_co_homogenus.dot(obj.matrix_world.transposed())[:, :3]

    pca = pca_mat(verts_co_world)
    center = verts_co_world.mean(axis=0)
    verts_co_world_shifted = verts_co_world - center
    verts_co_pca = verts_co_world_shifted.dot(np.linalg.inv(pca).T)
    dims_pca = np.ptp(verts_co_pca, axis=0)  # watchout for overflow

    new_mesh = bpy.data.meshes.new("")
    new_mesh.from_pydata(verts_co_pca, [], [])
    new_mesh.validate()
    new_obj = bpy.data.objects.new("", new_mesh)
    bpy.context.scene.collection.objects.link(new_obj)

    cylinders = []
    axes = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    for indices in ((0, 1, 2), (2, 0, 1), (0, 1, 2)):
        verts_co_pca_proj = verts_co_pca[:, indices]
        radius = np.sqrt((verts_co_pca_proj * verts_co_pca_proj).sum(axis=1)).max()
        depth = dims_pca[indices[2]]
        up = axes[indices[2]]
        cylinders.append(Cylinder(radius, depth, up))

    min_cylinder = min(cylinders, key=lambda c: c.calc_volume())
