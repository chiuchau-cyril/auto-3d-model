"""Quality Gate — Bolt hole positions satisfy geometry constraints."""

import math

import pytest

from src.models.flange_spec import FlangeSpecification
from src.services.dxf_builder import build_dxf_document
from src.lib.layers import HOLES


def _hole_centers(doc):
    msp = doc.modelspace()
    return [
        (e.dxf.center.x, e.dxf.center.y)
        for e in msp
        if e.dxftype() == "CIRCLE" and e.dxf.layer == HOLES.name
    ]


def _spec_for_count(count: int) -> FlangeSpecification:
    return FlangeSpecification(
        inner_diameter_mm=100.0,
        pcd_mm=150.0,
        outer_diameter_mm=200.0,
        bolt_hole_count=count,
        bolt_hole_diameter_mm=12.0,
        thickness_mm=20.0,
        material="SS400",
    )


@pytest.mark.parametrize("count", [1, 4, 8, 32])
def test_all_holes_on_pcd(count):
    spec = _spec_for_count(count)
    doc = build_dxf_document(spec)
    centers = _hole_centers(doc)
    expected_r = spec.pcd_mm / 2.0
    for x, y in centers:
        assert abs(math.hypot(x, y) - expected_r) < 1e-6


@pytest.mark.parametrize("count", [1, 4, 8, 32])
def test_first_hole_on_positive_x_axis(count):
    spec = _spec_for_count(count)
    doc = build_dxf_document(spec)
    # Sort by angle to find the "first" hole (angle closest to 0)
    centers = _hole_centers(doc)
    angles = [math.atan2(y, x) for x, y in centers]
    min_angle = min(angles, key=abs)
    assert abs(min_angle) < 1e-9


@pytest.mark.parametrize("count", [4, 8, 32])
def test_adjacent_angles_equal_2pi_over_count(count):
    spec = _spec_for_count(count)
    doc = build_dxf_document(spec)
    centers = _hole_centers(doc)
    angles = sorted(math.atan2(y, x) for x, y in centers)
    expected_step = 2 * math.pi / count
    for i in range(1, len(angles)):
        diff = angles[i] - angles[i - 1]
        assert abs(diff - expected_step) < 1e-9


def test_single_hole_count_one():
    spec = _spec_for_count(1)
    doc = build_dxf_document(spec)
    centers = _hole_centers(doc)
    assert len(centers) == 1
    x, y = centers[0]
    expected_r = spec.pcd_mm / 2.0
    assert abs(x - expected_r) < 1e-6
    assert abs(y) < 1e-6
