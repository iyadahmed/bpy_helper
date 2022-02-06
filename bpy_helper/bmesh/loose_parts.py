from typing import Callable, List

import bpy
import numpy as np
from mathutils import Vector

import bmesh

from .common import bmesh_to_object


class BMRegion:
    """Warning: this does not validate the BMesh, nor that the passed geometry belongs to same BMesh"""

    def __init__(
        self,
        verts: List[bmesh.types.BMVert],
        edges: List[bmesh.types.BMEdge],
        faces: List[bmesh.types.BMFace],
    ):
        self.verts = verts
        self.edges = edges
        self.faces = faces

        self._bb_min_cached = Vector()
        self._bb_max_cached = Vector()

    def update_bounding_box(self):
        co_arr = np.array([v.co for v in self.verts])
        min_bb = Vector(co_arr.min(axis=0))
        max_bb = Vector(co_arr.max(axis=0))

        self._bb_min_cached = min_bb
        self._bb_max_cached = max_bb

    @property
    def bb_max(self):
        """Cached"""
        return self._bb_max_cached

    @property
    def bb_min(self):
        """Cached"""
        return self._bb_min_cached

    @property
    def bb_mean(self) -> Vector:
        """Cached"""
        return 0.5 * (self.bb_min + self.bb_max)

    def to_obj(self, name):
        bm = bmesh.new(use_operators=False)
        self.to_bmesh(bm)
        obj = bmesh_to_object(bm, name)
        bm.free()
        return obj

    def to_bmesh(self, bm: bmesh.types.BMesh):
        vert_map = dict()
        for v in self.verts:
            vert_map[v] = bm.verts.new(v.co)

        for e in self.edges:
            bm.edges.new((vert_map[e.verts[0]], vert_map[e.verts[1]]))

        for f in self.faces:
            bm.faces.new([vert_map[v] for v in f.verts])


def _bm_grow_tagged(vert: bmesh.types.BMVert):
    """Flood fill untagged linked geometry starting from a vertex, tags and returns them"""
    verts = [vert]
    edges: List[bmesh.types.BMEdge] = []
    faces: List[bmesh.types.BMFace] = []

    for vert in verts:
        link_face: bmesh.types.BMFace
        for link_face in vert.link_faces:
            if link_face.tag:
                continue
            faces.append(link_face)
            link_face.tag = True
        link_edge: bmesh.types.BMEdge
        for link_edge in vert.link_edges:
            if link_edge.tag:
                continue
            link_edge.tag = True
            edges.append(link_edge)
            other_vert: bmesh.types.BMVert = link_edge.other_vert(vert)
            if other_vert.tag:
                continue
            verts.append(other_vert)
            other_vert.tag = True

        vert.tag = True

    # For debugging
    # assert len(set(verts)) == len(verts)
    # assert len(set(edges)) == len(edges)
    # assert len(set(faces)) == len(faces)

    return BMRegion(verts, edges, faces)


def _set_bmelem_tags_false_filter(elems, filter_func):
    """Sets tag for BMesh elements to False if they pass the filter (filter returns True),
    otherwise set tag to True, if filter is None, all tags are set to False"""
    if filter_func is None:
        for e in elems:
            e.tag = False
    else:
        # Defer setting of tags as filter might depend on original tag
        tag_values = dict()
        for e in elems:
            tag_values[e] = False if filter_func(e) else True
        for e in elems:
            e.tag = tag_values[e]


def bm_loose_parts(
    bm: bmesh.types.BMesh,
    verts_filter: Callable[[bmesh.types.BMVert], bool] = None,
    edges_filter: Callable[[bmesh.types.BMEdge], bool] = None,
    faces_filter: Callable[[bmesh.types.BMFace], bool] = None,
):
    assert bm
    assert bm.is_valid

    # Tag all elements as False to be included in the flood fill search,
    # if filter is not None, tags that pass the filter (filter returns True)
    # will be set to True so they don't get included in the search
    _set_bmelem_tags_false_filter(bm.verts, verts_filter)
    _set_bmelem_tags_false_filter(bm.edges, edges_filter)
    _set_bmelem_tags_false_filter(bm.faces, faces_filter)

    loose_parts: List[BMRegion] = []

    for seed_vert in bm.verts:
        if seed_vert.tag:
            continue
        # We could yield instead
        # but tag could be modifed after yield
        # so better to store results in a list
        loose_parts.append(_bm_grow_tagged(seed_vert))

    return loose_parts
