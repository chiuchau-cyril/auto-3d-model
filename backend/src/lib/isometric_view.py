"""Small tilted-disk inset (upper-right) showing the flange's thickness.

The main top-down view does not convey thickness. This adds a compact
3D-style view next to it. The cylinder axis lies *horizontally* — front
face on the right, back face on the left — so the thickness reads as a
left-right span.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from .layers import DIM, OUTLINE

if TYPE_CHECKING:
    from ezdxf.document import Drawing

    from src.models.flange_spec import FlangeSpecification


_TILT_RATIO = 0.45  # ellipse minor/major ratio (here: horizontal/vertical)
_ISO_SCALE = 0.32
_MIN_THICKNESS_FRACTION = 0.18


def _fmt_mm(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def add_isometric_inset(doc: "Drawing", spec: "FlangeSpecification") -> None:
    msp = doc.modelspace()
    outer_r_main = spec.outer_diameter_mm / 2.0

    big_r = (spec.outer_diameter_mm / 2.0) * _ISO_SCALE  # ellipse major (vertical)
    small_r = (spec.inner_diameter_mm / 2.0) * _ISO_SCALE
    minor_big = big_r * _TILT_RATIO  # how wide each ellipse is horizontally

    real_thickness = spec.thickness_mm * _ISO_SCALE
    min_thickness = minor_big * _MIN_THICKNESS_FRACTION
    iso_t = max(real_thickness, min_thickness)

    # Place inset clear of the main drawing and right-side annotations.
    cx = outer_r_main * 1.9
    cy = outer_r_main * 1.35
    left_cx = cx - iso_t / 2  # back face centre
    right_cx = cx + iso_t / 2  # front face centre

    outline_attribs = {"layer": OUTLINE.name, "color": OUTLINE.color}
    dim_attribs = {"layer": DIM.name, "color": DIM.color}

    # Outer cylinder: front (right) ellipse full, back (left) ellipse full so
    # the user reads it as a clear wireframe; top + bottom tangent lines bound
    # the cylindrical side.
    # major_axis=(0, big_r) means major axis is vertical (full diameter visible).
    msp.add_ellipse(
        center=(right_cx, cy),
        major_axis=(0, big_r),
        ratio=_TILT_RATIO,
        dxfattribs=outline_attribs,
    )
    msp.add_ellipse(
        center=(left_cx, cy),
        major_axis=(0, big_r),
        ratio=_TILT_RATIO,
        dxfattribs=outline_attribs,
    )
    msp.add_line((left_cx, cy + big_r), (right_cx, cy + big_r), dxfattribs=outline_attribs)
    msp.add_line((left_cx, cy - big_r), (right_cx, cy - big_r), dxfattribs=outline_attribs)

    # Inner bore: same treatment.
    msp.add_ellipse(
        center=(right_cx, cy),
        major_axis=(0, small_r),
        ratio=_TILT_RATIO,
        dxfattribs=outline_attribs,
    )
    msp.add_ellipse(
        center=(left_cx, cy),
        major_axis=(0, small_r),
        ratio=_TILT_RATIO,
        dxfattribs=outline_attribs,
    )
    msp.add_line((left_cx, cy + small_r), (right_cx, cy + small_r), dxfattribs=outline_attribs)
    msp.add_line((left_cx, cy - small_r), (right_cx, cy - small_r), dxfattribs=outline_attribs)

    # Horizontal dimension bracket below the inset.
    text_height = max(outer_r_main * 0.03, 1.4)
    bracket_y = cy - big_r - text_height * 1.8
    tick = text_height * 0.6
    # Horizontal span line.
    msp.add_line((left_cx, bracket_y), (right_cx, bracket_y), dxfattribs=dim_attribs)
    # End ticks.
    msp.add_line((left_cx, bracket_y - tick), (left_cx, bracket_y + tick), dxfattribs=dim_attribs)
    msp.add_line(
        (right_cx, bracket_y - tick), (right_cx, bracket_y + tick), dxfattribs=dim_attribs
    )
    # Short links from each ellipse bottom to the bracket.
    msp.add_line((left_cx, cy - big_r), (left_cx, bracket_y), dxfattribs=dim_attribs)
    msp.add_line((right_cx, cy - big_r), (right_cx, bracket_y), dxfattribs=dim_attribs)
    # Label centred below the bracket.
    label = f"t={_fmt_mm(spec.thickness_mm)}"
    msp.add_text(
        label,
        dxfattribs={
            **dim_attribs,
            "height": text_height,
            "insert": (cx - text_height * len(label) * 0.3, bracket_y - text_height * 1.6),
        },
    )
