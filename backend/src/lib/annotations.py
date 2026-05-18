"""English leader-line annotations + spec title block for the flange drawing.

Style follows the reference engineering drawing the customer provided:
- Three diameter leaders fanning out to the upper-right (outer / PCD / inner)
- One bolt-hole leader to the upper-left with combined "{count}-ø{dia}" notation
- A small title block in the lower-left listing all 7 spec fields

All on-drawing text is English per FR-025; the UI stays Traditional Chinese.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from .layers import ANNOTATION, DIM

if TYPE_CHECKING:
    from ezdxf.document import Drawing

    from src.models.flange_spec import FlangeSpecification

_DIA_SYM = "ø"


def _fmt_mm(value: float) -> str:
    """Render a mm value: drop ``.00`` on integers, trim trailing zeros otherwise."""
    if value == int(value):
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _text_height(outer_radius_mm: float) -> float:
    return max(outer_radius_mm * 0.04, 1.5)


def _diameter_leader(
    msp,
    *,
    circle_radius: float,
    angle_deg: float,
    outer_radius: float,
    label: str,
    text_height: float,
) -> None:
    """Slanted leader from a circle outward + horizontal shoulder + text."""
    ang = math.radians(angle_deg)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    leader_end_r = outer_radius * 1.4

    start = (circle_radius * cos_a, circle_radius * sin_a)
    end = (leader_end_r * cos_a, leader_end_r * sin_a)
    msp.add_line(start, end, dxfattribs={"layer": DIM.name, "color": DIM.color})

    shoulder_dir = 1.0 if cos_a >= 0 else -1.0
    shoulder_len = text_height * len(label) * 0.65
    shoulder_end = (end[0] + shoulder_dir * shoulder_len, end[1])
    msp.add_line(end, shoulder_end, dxfattribs={"layer": DIM.name, "color": DIM.color})

    text_x = end[0] + shoulder_dir * text_height * 0.4 if shoulder_dir > 0 else shoulder_end[0]
    msp.add_text(
        label,
        dxfattribs={
            "layer": DIM.name,
            "color": DIM.color,
            "height": text_height,
            "insert": (text_x, end[1] + text_height * 0.2),
        },
    )


def _bolt_hole_leader(
    msp,
    spec: "FlangeSpecification",
    outer_radius: float,
    text_height: float,
) -> None:
    """Leader from the bolt-hole nearest 135° to the upper-left."""
    pcd_r = spec.pcd_mm / 2.0
    hole_r = spec.bolt_hole_diameter_mm / 2.0

    # Snap to the actual hole closest to 135° (upper-left).
    target = 3 * math.pi / 4
    step = 2 * math.pi / spec.bolt_hole_count
    nearest_index = round(target / step) % spec.bolt_hole_count
    hole_angle = nearest_index * step
    cos_a, sin_a = math.cos(hole_angle), math.sin(hole_angle)

    # Touch the hole's outer edge along the radial direction.
    start = ((pcd_r + hole_r) * cos_a, (pcd_r + hole_r) * sin_a)
    leader_end_r = outer_radius * 1.4
    end = (leader_end_r * cos_a, leader_end_r * sin_a)
    msp.add_line(start, end, dxfattribs={"layer": DIM.name, "color": DIM.color})

    label = f"{spec.bolt_hole_count}-{_DIA_SYM}{_fmt_mm(spec.bolt_hole_diameter_mm)}"
    shoulder_len = text_height * len(label) * 0.65
    shoulder_end = (end[0] - shoulder_len, end[1])
    msp.add_line(end, shoulder_end, dxfattribs={"layer": DIM.name, "color": DIM.color})
    msp.add_text(
        label,
        dxfattribs={
            "layer": DIM.name,
            "color": DIM.color,
            "height": text_height,
            "insert": (shoulder_end[0], end[1] + text_height * 0.2),
        },
    )


def _title_block(
    msp,
    spec: "FlangeSpecification",
    outer_radius: float,
    text_height: float,
) -> None:
    """Spec listing below the drawing — keeps every field name searchable."""
    x = -outer_radius * 1.15
    y_start = -outer_radius * 1.25
    gap = text_height * 1.7
    lines = [
        f"Inner Diameter: {_DIA_SYM}{spec.inner_diameter_mm:.2f} mm",
        f"PCD: {_DIA_SYM}{spec.pcd_mm:.2f} mm",
        f"Outer Diameter: {_DIA_SYM}{spec.outer_diameter_mm:.2f} mm",
        f"Bolt Hole Count: {spec.bolt_hole_count}",
        f"Bolt Hole Diameter: {_DIA_SYM}{spec.bolt_hole_diameter_mm:.2f} mm",
        f"Thickness: {spec.thickness_mm:.2f} mm",
        f"Material: {spec.material}",
    ]
    for i, line in enumerate(lines):
        msp.add_text(
            line,
            dxfattribs={
                "layer": ANNOTATION.name,
                "color": ANNOTATION.color,
                "height": text_height,
                "insert": (x, y_start - i * gap),
            },
        )


def add_dimensions(doc: "Drawing", spec: "FlangeSpecification") -> None:
    msp = doc.modelspace()
    outer_r = spec.outer_diameter_mm / 2.0
    inner_r = spec.inner_diameter_mm / 2.0
    pcd_r = spec.pcd_mm / 2.0
    th = _text_height(outer_r)

    # Three diameter leaders fanning out to the upper-right.
    _diameter_leader(
        msp,
        circle_radius=outer_r,
        angle_deg=25,
        outer_radius=outer_r,
        label=f"{_DIA_SYM}{_fmt_mm(spec.outer_diameter_mm)}",
        text_height=th,
    )
    _diameter_leader(
        msp,
        circle_radius=pcd_r,
        angle_deg=40,
        outer_radius=outer_r,
        label=f"{_DIA_SYM}{_fmt_mm(spec.pcd_mm)} PCD",
        text_height=th,
    )
    _diameter_leader(
        msp,
        circle_radius=inner_r,
        angle_deg=55,
        outer_radius=outer_r,
        label=f"{_DIA_SYM}{_fmt_mm(spec.inner_diameter_mm)}",
        text_height=th,
    )

    # Bolt hole callout to the upper-left.
    _bolt_hole_leader(msp, spec, outer_r, th)

    # Title block (lower-left) listing all seven spec fields.
    _title_block(msp, spec, outer_r, th)
