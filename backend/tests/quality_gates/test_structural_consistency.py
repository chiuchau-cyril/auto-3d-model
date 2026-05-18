"""Quality Gate — Two builds from same spec produce identical structure."""

from collections import Counter

import pytest

from src.models.flange_spec import FlangeSpecification
from src.services.dxf_builder import build_dxf_document
from src.lib.layers import HOLES


def _entity_counts(doc):
    msp = doc.modelspace()
    return Counter((e.dxf.layer, e.dxftype()) for e in msp)


def _hole_centers(doc):
    msp = doc.modelspace()
    return sorted(
        (round(e.dxf.center.x, 9), round(e.dxf.center.y, 9))
        for e in msp
        if e.dxftype() == "CIRCLE" and e.dxf.layer == HOLES.name
    )


def test_layer_names_equal(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc1 = build_dxf_document(spec)
    doc2 = build_dxf_document(spec)
    layers1 = {layer.dxf.name for layer in doc1.layers}
    layers2 = {layer.dxf.name for layer in doc2.layers}
    assert layers1 == layers2


def test_entity_count_per_layer_type_equal(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc1 = build_dxf_document(spec)
    doc2 = build_dxf_document(spec)
    assert _entity_counts(doc1) == _entity_counts(doc2)


def test_hole_centers_equal(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc1 = build_dxf_document(spec)
    doc2 = build_dxf_document(spec)
    centers1 = _hole_centers(doc1)
    centers2 = _hole_centers(doc2)
    assert len(centers1) == len(centers2)
    for (x1, y1), (x2, y2) in zip(centers1, centers2):
        assert abs(x1 - x2) < 1e-9
        assert abs(y1 - y2) < 1e-9
