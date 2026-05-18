"""Filename builder per FR-017.

Format: flange_{inner}x{outer}_PCD{pcd}_{count}H_{thickness}t_{YYYYMMDDTHHMMSS}.{ext}
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.flange_spec import FlangeSpecification


def _fmt(value: float) -> str:
    """Render a mm value: integer if whole, else with up to 2 decimals."""
    if value == int(value):
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def build_filename(spec: "FlangeSpecification", ext: str, now: datetime | None = None) -> str:
    when = (now or datetime.utcnow()).strftime("%Y%m%dT%H%M%S")
    return (
        f"flange_{_fmt(spec.inner_diameter_mm)}x{_fmt(spec.outer_diameter_mm)}"
        f"_PCD{_fmt(spec.pcd_mm)}_{spec.bolt_hole_count}H"
        f"_{_fmt(spec.thickness_mm)}t_{when}.{ext.lstrip('.')}"
    )
