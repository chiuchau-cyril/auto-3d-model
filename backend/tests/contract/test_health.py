"""T022 — GET /api/health contract tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_health_returns_200():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/health")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_health_json_keys():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/health")
    body = r.json()
    assert "status" in body
    assert "oda_converter_available" in body
    assert "version" in body


@pytest.mark.asyncio
async def test_health_status_ok():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/health")
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health_oda_available_is_bool():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/health")
    assert isinstance(r.json()["oda_converter_available"], bool)
