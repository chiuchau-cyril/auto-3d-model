"""T038 — POST /api/flange/pdf contract tests."""

import io

import pypdf
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_pdf_valid_spec_200(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/pdf", json=valid_spec_kwargs)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_pdf_content_type(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/pdf", json=valid_spec_kwargs)
    assert r.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_pdf_body_starts_with_pdf_magic(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/pdf", json=valid_spec_kwargs)
    assert r.content[:5] == b"%PDF-"


@pytest.mark.asyncio
async def test_pdf_content_disposition_has_filename(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/pdf", json=valid_spec_kwargs)
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd
    assert "flange_" in cd


@pytest.mark.asyncio
async def test_pdf_page_count_is_one(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/pdf", json=valid_spec_kwargs)
    reader = pypdf.PdfReader(io.BytesIO(r.content))
    assert len(reader.pages) == 1  # FR-016 A4 portrait single page


@pytest.mark.asyncio
async def test_pdf_invalid_spec_400(valid_spec_kwargs):
    bad = dict(valid_spec_kwargs)
    bad["pcd_mm"] = bad["inner_diameter_mm"]  # geometry violation
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/pdf", json=bad)
    assert r.status_code == 400
