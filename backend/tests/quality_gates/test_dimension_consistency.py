"""Quality Gate — DXF geometry matches input spec within 0.01 mm (FR-019)."""

import math

import pytest

from src.models.flange_spec import FlangeSpecification
from src.services.dxf_builder import build_dxf_document
from src.lib.layers import HOLES, OUTLINE


def _outline_radii(doc):
    msp = doc.modelspace()
    return sorted(
        e.dxf.radius
        for e in msp
        if e.dxftype() == "CIRCLE" and e.dxf.layer == OUTLINE.name
    )


def _hole_centers(doc):
    msp = doc.modelspace()
    return [
        (e.dxf.center.x, e.dxf.center.y)
        for e in msp
        if e.dxftype() == "CIRCLE" and e.dxf.layer == HOLES.name
    ]


def test_outer_radius_matches_spec(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    radii = _outline_radii(doc)
    expected_outer = spec.outer_diameter_mm / 2.0
    assert abs(max(radii) - expected_outer) < 0.01


def test_inner_radius_matches_spec(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    radii = _outline_radii(doc)
    expected_inner = spec.inner_diameter_mm / 2.0
    assert abs(min(radii) - expected_inner) < 0.01


def test_hole_pcd_matches_spec(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    centers = _hole_centers(doc)
    expected_pcd_r = spec.pcd_mm / 2.0
    for x, y in centers:
        dist = math.hypot(x, y)
        assert abs(dist - expected_pcd_r) < 0.01


def test_hole_radius_matches_spec(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    msp = doc.modelspace()
    hole_circles = [
        e for e in msp
        if e.dxftype() == "CIRCLE" and e.dxf.layer == HOLES.name
    ]
    expected_hole_r = spec.bolt_hole_diameter_mm / 2.0
    for circle in hole_circles:
        assert abs(circle.dxf.radius - expected_hole_r) < 0.01
