"""DXF layer constants per data-model.md & Constitution III."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LayerSpec:
    name: str
    color: int  # AutoCAD Color Index
    linetype: str  # CONTINUOUS / DASHED / etc.


OUTLINE = LayerSpec(name="OUTLINE", color=7, linetype="CONTINUOUS")
HOLES = LayerSpec(name="HOLES", color=7, linetype="CONTINUOUS")
CENTERLINE = LayerSpec(name="CENTERLINE", color=1, linetype="DASHED")
DIM = LayerSpec(name="DIM", color=2, linetype="CONTINUOUS")
ANNOTATION = LayerSpec(name="ANNOTATION", color=3, linetype="CONTINUOUS")
WATERMARK = LayerSpec(name="WATERMARK", color=8, linetype="CONTINUOUS")

ALL_LAYERS: tuple[LayerSpec, ...] = (
    OUTLINE,
    HOLES,
    CENTERLINE,
    DIM,
    ANNOTATION,
    WATERMARK,
)
