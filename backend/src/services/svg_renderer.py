"""Render a DXF Drawing to SVG bytes via ezdxf's native SVG backend.

ezdxf converts TEXT entities to vector paths during rendering, so the
resulting SVG looks correct but its annotations are not selectable text.
To keep annotations searchable (tests / PDF embedding / accessibility) we
extract the TEXT entities from the source document and inject them as a
hidden <g> overlay carrying the plain strings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ezdxf.addons.drawing import Frontend, RenderContext, layout
from ezdxf.addons.drawing.svg import SVGBackend

if TYPE_CHECKING:
    from ezdxf.document import Drawing


def _extract_text_lines(doc: "Drawing") -> list[str]:
    msp = doc.modelspace()
    return [e.dxf.text for e in msp.query("TEXT") if e.dxf.text]


def _inject_searchable_text(svg_xml: str, lines: list[str]) -> str:
    """Append a hidden <g> with <text> children inside the closing </svg> tag.

    Hidden via visibility:hidden so visual rendering is unchanged; the strings
    remain in the DOM/string for grep / accessibility / PDF text extraction.
    """
    if not lines:
        return svg_xml
    escaped = (
        line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        for line in lines
    )
    overlay = (
        '<g style="visibility:hidden" font-size="0" data-spec-overlay="true">'
        + "".join(f"<text>{t}</text>" for t in escaped)
        + "</g>"
    )
    close = "</svg>"
    idx = svg_xml.rfind(close)
    if idx == -1:
        return svg_xml + overlay
    return svg_xml[:idx] + overlay + svg_xml[idx:]


def render_svg(doc: "Drawing") -> bytes:
    msp = doc.modelspace()
    ctx = RenderContext(doc)
    backend = SVGBackend()
    Frontend(ctx, backend).draw_layout(msp, finalize=True)

    page = layout.Page(width=210, height=210, units=layout.Units.mm)
    xml = backend.get_string(page)
    xml_with_text = _inject_searchable_text(xml, _extract_text_lines(doc))
    return xml_with_text.encode("utf-8")
