from typing import Dict, List

from mathutils import Vector

import bmesh
from bmesh.types import BMEdge, BMesh, BMFace, BMVert


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

            nv0 = vert_map[e.verts[0]]
            nv1 = vert_map[e.verts[1]]
            bm.faces.new((e.verts[1], e.verts[0], nv0, nv1))
            e.tag = True

        new_face = bm.faces.new(new_verts)
        wavefront_faces.append(new_face)

    if delete_input_faces:
        bmesh.ops.delete(bm, geom=faces_to_be_extruded, context="FACES")

    return wavefront_faces


def bm_extrude_faces_move_steps(bm: BMesh, faces_to_be_extruded: List[BMFace], translation: Vector, num_steps: int):
    total_distance = translation.length
    extrude_normal = translation / total_distance
    if num_steps < 1:
        return
    step_distance = total_distance / num_steps
    extrude_translation = extrude_normal * step_distance
    for _ in range(num_steps):
        faces_to_be_extruded, _ = bm_extrude_faces_move(bm, faces_to_be_extruded, extrude_translation)
