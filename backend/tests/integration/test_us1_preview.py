"""T024 — US1 SVG preview integration tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_preview_svg_contains_ss400(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/preview", json=valid_spec_kwargs)
    assert b"SS400" in r.content


@pytest.mark.asyncio
async def test_preview_svg_contains_watermark(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/preview", json=valid_spec_kwargs)
    assert b"For Customer Preview Only" in r.content


@pytest.mark.asyncio
async def test_preview_svg_contains_all_field_labels(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/preview", json=valid_spec_kwargs)
    text = r.content
    # Each of the 7 spec field data values must appear
    assert b"100" in text   # inner_diameter_mm
    assert b"150" in text   # pcd_mm
    assert b"200" in text   # outer_diameter_mm
    assert b"8" in text     # bolt_hole_count
    assert b"12" in text    # bolt_hole_diameter_mm
    assert b"20" in text    # thickness_mm
    assert b"SS400" in text # material


@pytest.mark.asyncio
async def test_preview_structural_consistency(valid_spec_kwargs):
    """Two identical requests return identically-sized SVG responses."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r1 = await ac.post("/api/flange/preview", json=valid_spec_kwargs)
        r2 = await ac.post("/api/flange/preview", json=valid_spec_kwargs)
    assert len(r1.content) == len(r2.content)
