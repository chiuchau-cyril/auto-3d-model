"""Watermark text and helpers shared by DWG / SVG / PDF outputs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .layers import WATERMARK

if TYPE_CHECKING:
    from ezdxf.document import Drawing


WATERMARK_TEXT = "For Customer Preview Only — Not for Manufacturing"


def insert_dxf_watermark(doc: "Drawing", radius_mm: float) -> None:
    """Insert watermark text into the WATERMARK layer of `doc`.

    The text is rotated -30 degrees and sized relative to the flange radius
    so it remains visible on both tiny and huge flanges.
    """
    msp = doc.modelspace()
    text_height = max(radius_mm * 0.08, 2.0)
    msp.add_text(
        WATERMARK_TEXT,
        dxfattribs={
            "layer": WATERMARK.name,
            "height": text_height,
            "color": WATERMARK.color,
            "rotation": -30,
            "insert": (-radius_mm * 0.9, 0),
        },
    )
