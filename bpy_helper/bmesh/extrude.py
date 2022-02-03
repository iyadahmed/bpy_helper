from typing import Dict, List, Set

from mathutils import Vector

import bmesh
from bmesh.types import BMEdge, BMesh, BMFace, BMVert


def _bm_creat_edge_unique(bm: BMesh, v0: BMVert, v1: BMVert):
    e: BMEdge
    for e in v0.link_edges:
        if e.other_vert(v0) == v1:
            return e
    return bm.edges.new((v0, v1))


def bm_extrude_faces_move(
    bm: BMesh,
    faces_to_be_extruded: List[BMFace],
    translation: Vector,
    delete_input_faces: bool = True,
):
    for f in bm.faces:
        f.tag = False

    for f in faces_to_be_extruded:
        f.tag = True
        for v in f.verts:
            v.tag = False
        for e in f.edges:
            e.tag = False

    v: BMVert
    e: BMEdge
    f: BMFace

    wavefront_faces: List[BMFace] = []
    side_edge_ring: Set[BMEdge] = set()
    vert_map: Dict[BMVert, BMVert] = dict()  # Maps verts to extruded verts

    for f in faces_to_be_extruded:
        new_verts = [None] * len(f.verts)
        for i, v in enumerate(f.verts):
            if not v.tag:
                new_vert = bm.verts.new(v.co + translation)
                vert_map[v] = new_vert
                v.tag = True
            else:
                new_vert = vert_map[v]
            new_verts[i] = new_vert

        # Extrude extrusion faces edge boundary
        for e in f.edges:
            if e.tag:
                continue
            # TODO: support edges with more than two linked faces
            is_extrusion_boundary = len([f for f in e.link_faces if f.tag]) == 1
            if not is_extrusion_boundary:
                continue

            v0 = e.verts[0]
            v1 = e.verts[1]
            nv0 = vert_map[v0]
            nv1 = vert_map[v1]

            se0 = _bm_creat_edge_unique(bm, v0, nv0)
            se1 = _bm_creat_edge_unique(bm, v1, nv1)
            side_edge_ring.update((se0, se1))

            bm.faces.new((v1, v0, nv0, nv1))
            e.tag = True

        new_face = bm.faces.new(new_verts)
        wavefront_faces.append(new_face)

    if delete_input_faces:
        bmesh.ops.delete(bm, geom=faces_to_be_extruded, context="FACES")

    return wavefront_faces, side_edge_ring


def bm_extrude_faces_move_steps(bm: BMesh, faces_to_be_extruded: List[BMFace], translation: Vector, num_steps: int):
    _, side_edge_ring = bm_extrude_faces_move(bm, faces_to_be_extruded, translation)
    bmesh.ops.subdivide_edgering(bm, edges=list(side_edge_ring), interp_mode="LINEAR", smooth=0.0, cuts=num_steps)
