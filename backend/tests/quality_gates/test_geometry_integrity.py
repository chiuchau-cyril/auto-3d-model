"""Quality Gate — DXF audit clean, correct circle counts per layer."""

import pytest

from src.models.flange_spec import FlangeSpecification
from src.services.dxf_builder import build_dxf_document
from src.lib.layers import HOLES, OUTLINE


def test_dxf_audit_no_errors(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    auditor = doc.audit()
    assert auditor.errors == []


def test_outline_circle_count_is_two(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    msp = doc.modelspace()
    outline_circles = [
        e for e in msp
        if e.dxftype() == "CIRCLE" and e.dxf.layer == OUTLINE.name
    ]
    assert len(outline_circles) == 2


def test_holes_circle_count_matches_spec(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    msp = doc.modelspace()
    hole_circles = [
        e for e in msp
        if e.dxftype() == "CIRCLE" and e.dxf.layer == HOLES.name
    ]
    assert len(hole_circles) == spec.bolt_hole_count


@pytest.mark.parametrize("count", [1, 4, 8, 16])
def test_holes_circle_count_parametric(count, valid_spec_kwargs):
    kwargs = dict(valid_spec_kwargs)
    kwargs["bolt_hole_count"] = count
    spec = FlangeSpecification(**kwargs)
    doc = build_dxf_document(spec)
    msp = doc.modelspace()
    hole_circles = [
        e for e in msp
        if e.dxftype() == "CIRCLE" and e.dxf.layer == HOLES.name
    ]
    assert len(hole_circles) == count
