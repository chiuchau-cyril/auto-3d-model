"""Geometry helpers for flange layout.

Coordinate system: origin at flange centre, Z perpendicular to flange face,
first hole at 0 deg on the +X axis (Constitution II).
"""

import math


def bolt_hole_positions(pcd_mm: float, count: int) -> list[tuple[float, float]]:
    """Return (x, y) centres of bolt holes evenly distributed on PCD.

    The first hole sits at angle 0 (i.e. on the +X axis); subsequent holes
    proceed counter-clockwise.
    """
    if count < 1:
        raise ValueError("count must be >= 1")
    if pcd_mm <= 0:
        raise ValueError("pcd_mm must be > 0")

    radius = pcd_mm / 2.0
    step = 2 * math.pi / count
    return [(radius * math.cos(i * step), radius * math.sin(i * step)) for i in range(count)]
