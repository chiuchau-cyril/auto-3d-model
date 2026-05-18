"""Render an A4 portrait single-page PDF: drawing + spec table + watermark + timestamp.

The whole story MUST fit on one A4 page (FR-016). Heights are tight: a
typical A4 with 14 mm margins leaves ~269 mm of usable height. We cap the
embedded SVG at 130 mm so the spec table + footer always fit below it.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import TYPE_CHECKING

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from svglib.svglib import svg2rlg

from src.lib.watermark import WATERMARK_TEXT

if TYPE_CHECKING:
    from src.models.flange_spec import FlangeSpecification


_PAGE_W, _PAGE_H = A4
_MARGIN = 14 * mm
_MAX_DRAWING_HEIGHT = 130 * mm


def _watermark_canvas(canvas, _doc):  # noqa: ANN001 — reportlab callback signature
    canvas.saveState()
    canvas.setFont("Helvetica", 36)
    canvas.setFillColor(colors.Color(0.5, 0.5, 0.5, alpha=0.18))
    canvas.translate(_PAGE_W / 2, _PAGE_H / 2)
    canvas.rotate(35)
    canvas.drawCentredString(0, 0, WATERMARK_TEXT)
    canvas.restoreState()


def _build_spec_table(spec: "FlangeSpecification") -> Table:
    rows = [
        ["Specification", "Value"],
        ["Inner Diameter", f"O/ {spec.inner_diameter_mm:.2f} mm"],
        ["PCD", f"O/ {spec.pcd_mm:.2f} mm"],
        ["Outer Diameter", f"O/ {spec.outer_diameter_mm:.2f} mm"],
        ["Bolt Hole Count", str(spec.bolt_hole_count)],
        ["Bolt Hole Diameter", f"O/ {spec.bolt_hole_diameter_mm:.2f} mm"],
        ["Thickness", f"{spec.thickness_mm:.2f} mm"],
        ["Material", spec.material],
    ]
    table = Table(rows, colWidths=[55 * mm, 70 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
            ]
        )
    )
    return table


def render_pdf(spec: "FlangeSpecification", svg_bytes: bytes) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=_MARGIN,
        bottomMargin=_MARGIN,
        title="Flange Preview",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "FlangeTitle", parent=styles["Title"], fontSize=14, leading=16, spaceAfter=4
    )
    heading_style = ParagraphStyle(
        "FlangeHeading",
        parent=styles["Heading2"],
        fontSize=11,
        leading=13,
        spaceBefore=2,
        spaceAfter=2,
    )
    footer_style = ParagraphStyle(
        "FlangeFooter", parent=styles["BodyText"], fontSize=8, leading=10
    )

    story = []
    story.append(Paragraph("Flange Drawing", title_style))

    drawing = svg2rlg(io.BytesIO(svg_bytes))
    if drawing is not None and drawing.width and drawing.height:
        available_w = _PAGE_W - 2 * _MARGIN
        scale = min(available_w / drawing.width, _MAX_DRAWING_HEIGHT / drawing.height)
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)
        story.append(drawing)

    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Specification", heading_style))
    story.append(_build_spec_table(spec))
    story.append(Spacer(1, 3 * mm))

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    story.append(
        Paragraph(
            f"Generated: {now}<br/>"
            f"<font color='#888888'>{WATERMARK_TEXT}</font>",
            footer_style,
        )
    )

    doc.build(story, onFirstPage=_watermark_canvas, onLaterPages=_watermark_canvas)
    return buf.getvalue()
