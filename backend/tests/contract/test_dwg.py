"""T037 — POST /api/flange/dwg contract tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import oda_skip
from src.main import app


@oda_skip
@pytest.mark.asyncio
async def test_dwg_valid_spec_200(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/dwg", json=valid_spec_kwargs)
    assert r.status_code == 200


@oda_skip
@pytest.mark.asyncio
async def test_dwg_content_type(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/dwg", json=valid_spec_kwargs)
    assert r.headers["content-type"] == "application/acad"


@oda_skip
@pytest.mark.asyncio
async def test_dwg_content_disposition_filename(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/dwg", json=valid_spec_kwargs)
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd
    assert "flange_" in cd


@oda_skip
@pytest.mark.asyncio
async def test_dwg_body_starts_with_ac1015_magic(valid_spec_kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/dwg", json=valid_spec_kwargs)
    assert r.content[:6] == b"AC1015"


@pytest.mark.asyncio
async def test_dwg_invalid_spec_400(valid_spec_kwargs):
    bad = dict(valid_spec_kwargs)
    bad["pcd_mm"] = bad["inner_diameter_mm"]  # geometry violation
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/flange/dwg", json=bad)
    assert r.status_code == 400
