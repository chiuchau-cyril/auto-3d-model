"""Build a single ezdxf Drawing that is the source of truth for SVG/DWG/PDF.

Constitution alignment:
- II  Units mm ($INSUNITS = 4); bolt holes evenly distributed from 0 deg on +X.
- III Layers + origin at flange centre, drawing version R2000.
- IV  Validation already enforced upstream by FlangeSpecification.
- V   Same input -> same DXF structure -> same downstream renderings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import ezdxf
from ezdxf.document import Drawing

from src.lib.annotations import add_dimensions
from src.lib.geometry import bolt_hole_positions
from src.lib.layers import ALL_LAYERS, CENTERLINE, HOLES, OUTLINE
from src.lib.watermark import insert_dxf_watermark

if TYPE_CHECKING:
    from src.models.flange_spec import FlangeSpecification


def _ensure_layers(doc: Drawing) -> None:
    for spec in ALL_LAYERS:
        if spec.name not in doc.layers:
            doc.layers.add(name=spec.name, color=spec.color, linetype=spec.linetype)


def _ensure_linetypes(doc: Drawing) -> None:
    # DASHED is a built-in linetype in ezdxf standard templates.
    if "DASHED" not in doc.linetypes:
        doc.linetypes.add(
            "DASHED",
            pattern="A,.5,-.25",
            description="Dashed __ __ __ __ __ __ __ __ __ __ __ __ __ _",
        )


def build_dxf_document(spec: "FlangeSpecification") -> Drawing:
    doc = ezdxf.new(dxfversion="R2000", setup=True)
    doc.header["$INSUNITS"] = 4  # millimeters
    _ensure_linetypes(doc)
    _ensure_layers(doc)

    msp = doc.modelspace()
    outer_r = spec.outer_diameter_mm / 2.0
    inner_r = spec.inner_diameter_mm / 2.0
    pcd_r = spec.pcd_mm / 2.0
    hole_r = spec.bolt_hole_diameter_mm / 2.0

    # Outline (outer + inner circle)
    msp.add_circle(center=(0, 0), radius=outer_r, dxfattribs={"layer": OUTLINE.name})
    msp.add_circle(center=(0, 0), radius=inner_r, dxfattribs={"layer": OUTLINE.name})

    # PCD reference (dashed) + centre crosshair
    msp.add_circle(
        center=(0, 0),
        radius=pcd_r,
        dxfattribs={"layer": CENTERLINE.name, "linetype": "DASHED"},
    )
    cross = outer_r * 1.1
    msp.add_line((-cross, 0), (cross, 0), dxfattribs={"layer": CENTERLINE.name})
    msp.add_line((0, -cross), (0, cross), dxfattribs={"layer": CENTERLINE.name})

    # Bolt holes evenly distributed from 0 deg on +X
    for x, y in bolt_hole_positions(spec.pcd_mm, spec.bolt_hole_count):
        msp.add_circle(center=(x, y), radius=hole_r, dxfattribs={"layer": HOLES.name})

    # Dimensions + spec annotations (English) and watermark
    add_dimensions(doc, spec)
    insert_dxf_watermark(doc, radius_mm=outer_r)

    return doc
