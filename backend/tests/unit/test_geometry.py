import math

import pytest

from src.lib.geometry import bolt_hole_positions


def test_single_hole_at_origin_of_x_axis():
    pts = bolt_hole_positions(pcd_mm=100, count=1)
    assert len(pts) == 1
    x, y = pts[0]
    assert math.isclose(x, 50.0, abs_tol=1e-9)
    assert math.isclose(y, 0.0, abs_tol=1e-9)


def test_four_holes_equally_distributed():
    pts = bolt_hole_positions(pcd_mm=200, count=4)
    assert len(pts) == 4
    # First on +X
    assert math.isclose(pts[0][0], 100.0)
    assert math.isclose(pts[0][1], 0.0, abs_tol=1e-9)
    # Second on +Y
    assert math.isclose(pts[1][0], 0.0, abs_tol=1e-9)
    assert math.isclose(pts[1][1], 100.0)


def test_eight_holes_radius_consistent():
    pts = bolt_hole_positions(pcd_mm=150, count=8)
    radii = [math.hypot(x, y) for x, y in pts]
    assert all(math.isclose(r, 75.0, abs_tol=1e-9) for r in radii)


def test_sixty_four_holes_step_uniform():
    pts = bolt_hole_positions(pcd_mm=500, count=64)
    angles = [math.atan2(y, x) for x, y in pts]
    diffs = [(angles[i + 1] - angles[i]) % (2 * math.pi) for i in range(len(angles) - 1)]
    expected = 2 * math.pi / 64
    assert all(math.isclose(d, expected, abs_tol=1e-9) for d in diffs)


def test_invalid_input_raises():
    with pytest.raises(ValueError):
        bolt_hole_positions(pcd_mm=0, count=4)
    with pytest.raises(ValueError):
        bolt_hole_positions(pcd_mm=100, count=0)
