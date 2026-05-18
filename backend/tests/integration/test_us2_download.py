"""T040 — US2 DWG/PDF download integration tests."""

import io

import pypdf
import pytest

from tests.conftest import oda_skip
from src.models.flange_spec import FlangeSpecification
from src.services.dxf_builder import build_dxf_document
from src.services.dwg_exporter import export_dwg
from src.services.pdf_renderer import render_pdf
from src.services.svg_renderer import render_svg


@oda_skip
def test_dwg_has_ac1015_magic(valid_spec_kwargs):
    """DWG is a binary proprietary format; verify via the 6-byte version header."""
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    dwg_bytes = export_dwg(doc)
    assert dwg_bytes[:6] == b"AC1015"


def test_pdf_openable_by_pypdf(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    svg = render_svg(doc)
    pdf_bytes = render_pdf(spec, svg)

    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) == 1  # FR-016 A4 portrait single page


def test_pdf_page1_contains_ss400_or_watermark(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    svg = render_svg(doc)
    pdf_bytes = render_pdf(spec, svg)

    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    text = reader.pages[0].extract_text() or ""
    assert "SS400" in text or "For Customer Preview Only" in text
