"""T021 — POST /api/flange/preview contract tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_preview_valid_spec_200(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/preview", json=valid_spec_kwargs)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_preview_content_type_svg(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/preview", json=valid_spec_kwargs)
    assert r.headers["content-type"].startswith("image/svg+xml")


@pytest.mark.asyncio
async def test_preview_body_contains_svg_tag(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/preview", json=valid_spec_kwargs)
    assert b"<svg" in r.content


@pytest.mark.asyncio
async def test_preview_body_length_exceeds_1000(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/preview", json=valid_spec_kwargs)
    assert len(r.content) > 1000


@pytest.mark.asyncio
async def test_preview_missing_field_400():
    payload = {
        "pcd_mm": 150.0,
        "outer_diameter_mm": 200.0,
        "bolt_hole_count": 8,
        "bolt_hole_diameter_mm": 12.0,
        "thickness_mm": 20.0,
        "material": "SS400",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/preview", json=payload)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_preview_pcd_le_inner_diameter_400(valid_spec_kwargs):
    bad = dict(valid_spec_kwargs)
    bad["pcd_mm"] = bad["inner_diameter_mm"]  # pcd == inner — violates constraint
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/preview", json=bad)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_preview_bolt_hole_overflow_400(valid_spec_kwargs):
    bad = dict(valid_spec_kwargs)
    # max_hole = min((200-150)/2, (150-100)/2) = 25 — use value >= 25
    bad["bolt_hole_diameter_mm"] = 25.0
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/preview", json=bad)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_preview_error_response_shape(valid_spec_kwargs):
    bad = dict(valid_spec_kwargs)
    bad["pcd_mm"] = bad["inner_diameter_mm"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/preview", json=bad)
    body = r.json()
    assert "errors" in body
    assert isinstance(body["errors"], list)
    assert len(body["errors"]) > 0
    for err in body["errors"]:
        assert "field" in err
        assert "message" in err
        assert isinstance(err["field"], str)
        assert isinstance(err["message"], str)
