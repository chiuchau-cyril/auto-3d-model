"""T056 — Edge case integration tests."""

import math

import pytest
from pydantic import ValidationError

from src.models.flange_spec import FlangeSpecification
from src.services.dxf_builder import build_dxf_document
from src.services.svg_renderer import render_svg
from src.lib.layers import HOLES


def _hole_centers(doc):
    msp = doc.modelspace()
    return [
        (e.dxf.center.x, e.dxf.center.y)
        for e in msp
        if e.dxftype() == "CIRCLE" and e.dxf.layer == HOLES.name
    ]


def test_tiny_flange_builds_dxf():
    spec = FlangeSpecification(
        inner_diameter_mm=1.0,
        pcd_mm=3.0,
        outer_diameter_mm=5.0,
        bolt_hole_count=1,
        bolt_hole_diameter_mm=0.5,
        thickness_mm=2.0,
        material="SS400",
    )
    doc = build_dxf_document(spec)
    assert doc is not None


def test_tiny_flange_renders_svg():
    spec = FlangeSpecification(
        inner_diameter_mm=1.0,
        pcd_mm=3.0,
        outer_diameter_mm=5.0,
        bolt_hole_count=1,
        bolt_hole_diameter_mm=0.5,
        thickness_mm=2.0,
        material="SS400",
    )
    doc = build_dxf_document(spec)
    svg = render_svg(doc)
    assert b"<svg" in svg


def test_large_flange_builds_dxf():
    spec = FlangeSpecification(
        inner_diameter_mm=500.0,
        pcd_mm=750.0,
        outer_diameter_mm=1000.0,
        bolt_hole_count=32,
        bolt_hole_diameter_mm=30.0,
        thickness_mm=50.0,
        material="SS400",
    )
    doc = build_dxf_document(spec)
    assert doc is not None


def test_large_flange_renders_svg():
    spec = FlangeSpecification(
        inner_diameter_mm=500.0,
        pcd_mm=750.0,
        outer_diameter_mm=1000.0,
        bolt_hole_count=32,
        bolt_hole_diameter_mm=30.0,
        thickness_mm=50.0,
        material="SS400",
    )
    doc = build_dxf_document(spec)
    svg = render_svg(doc)
    assert b"<svg" in svg


def test_single_hole_count_one_entity_at_positive_x():
    spec = FlangeSpecification(
        inner_diameter_mm=100.0,
        pcd_mm=150.0,
        outer_diameter_mm=200.0,
        bolt_hole_count=1,
        bolt_hole_diameter_mm=12.0,
        thickness_mm=20.0,
        material="SS400",
    )
    doc = build_dxf_document(spec)
    centers = _hole_centers(doc)
    assert len(centers) == 1
    x, y = centers[0]
    expected_r = spec.pcd_mm / 2.0
    assert abs(x - expected_r) < 1e-6
    assert abs(y) < 1e-6


def test_many_holes_count_64_all_on_pcd():
    spec = FlangeSpecification(
        inner_diameter_mm=100.0,
        pcd_mm=150.0,
        outer_diameter_mm=200.0,
        bolt_hole_count=64,
        bolt_hole_diameter_mm=2.0,
        thickness_mm=20.0,
        material="SS400",
    )
    doc = build_dxf_document(spec)
    centers = _hole_centers(doc)
    assert len(centers) == 64
    expected_r = spec.pcd_mm / 2.0
    for x, y in centers:
        assert abs(math.hypot(x, y) - expected_r) < 1e-6


def test_hole_overflow_raises_validation_error():
    with pytest.raises(ValidationError):
        FlangeSpecification(
            inner_diameter_mm=100.0,
            pcd_mm=150.0,
            outer_diameter_mm=200.0,
            bolt_hole_count=8,
            bolt_hole_diameter_mm=25.0,  # max_hole = 25, must be < 25
            thickness_mm=20.0,
            material="SS400",
        )
