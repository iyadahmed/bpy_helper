import bmesh
from typing import List
from mathutils import Vector


def bm_extrude_faces_move(bm: bmesh.types.BMesh, faces_to_be_extruded: List[bmesh.types.BMFace], translation: Vector):
    extrude_map = dict()

    for f in bm.faces:
        f.tag = False

    for f in faces_to_be_extruded:
        f.tag = True

    verts_to_be_extruded = set(v for f in faces_to_be_extruded for v in f.verts)
    edges_to_be_extruded = set(e for f in faces_to_be_extruded for e in f.edges)

    v: bmesh.types.BMVert
    e: bmesh.types.BMEdge
    f: bmesh.types.BMFace

    wavefront_faces: List[bmesh.types.BMFace] = []

    for v in verts_to_be_extruded:
        new_vert = bm.verts.new(v.co + translation)
        extrude_map[v] = new_vert
        if len([f for f in v.link_faces if f.tag]) == 0:
            bm.edges.new((v, new_vert))

    for e in edges_to_be_extruded:
        is_extrusion_boundary = len([f for f in e.link_faces if f.tag]) == 1
        if e.is_wire or is_extrusion_boundary:
            new_edge = bm.edges.new([extrude_map[v] for v in e.verts])
            extrude_map[e] = new_edge
            face = bm.faces.new((*reversed(e.verts), *new_edge.verts))
            face.normal_update()

    for f in faces_to_be_extruded:
        new_face = bm.faces.new([extrude_map[v] for v in f.verts])
        new_face.normal_update()
        extrude_map[f] = new_face
        wavefront_faces.append(new_face)

    bmesh.ops.delete(bm, geom=faces_to_be_extruded, context="FACES")
    return wavefront_faces


def bm_extrude_face_move_steps(
    bm: bmesh.types.BMesh,
    faces_to_be_extruded: List[bmesh.types.BMFace],
    total_distance: float,
    step_distance: float,
    extrude_normal: Vector,
):
    if abs(total_distance) < 0.000001:
        return
    extrude_normal.normalize()
    step_distance = min(step_distance, total_distance)
    if abs(step_distance) < 0.0000001:
        extrude_count = 1
        true_extrude_distance = total_distance
    else:
        extrude_count = int(total_distance / step_distance)
        true_extrude_distance = total_distance / extrude_count

    extrude_translation = extrude_normal * true_extrude_distance
    for _ in range(extrude_count):
        faces_to_be_extruded = bm_extrude_faces_move(bm, faces_to_be_extruded, extrude_translation)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
