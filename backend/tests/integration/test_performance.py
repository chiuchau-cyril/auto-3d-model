"""Performance / SLO tests — T057.

Verifies SC-002 (preview p95 ≤ 5 000 ms) and SC-003 (DWG/PDF p95 ≤ 3 000 ms).

Run with:
    pytest tests/integration/test_performance.py -v -m slow

These tests are intentionally excluded from the default run (pytest -m "not slow").
"""

from __future__ import annotations

import os
import statistics
import time
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from tests.conftest import oda_skip

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_SPEC = {
    "inner_diameter_mm": 100.0,
    "pcd_mm": 150.0,
    "outer_diameter_mm": 200.0,
    "bolt_hole_count": 8,
    "bolt_hole_diameter_mm": 12.0,
    "thickness_mm": 20.0,
    "material": "SS400",
}

N_SAMPLES = 20


def _percentile(data: list[float], pct: float) -> float:
    """Return the p-th percentile of *data* (0–100 scale, exclusive method)."""
    return statistics.quantiles(data, n=100, method="exclusive")[int(pct) - 1]


def _print_stats(endpoint: str, samples_ms: list[float]) -> None:
    p50 = _percentile(samples_ms, 50)
    p95 = _percentile(samples_ms, 95)
    p99 = _percentile(samples_ms, 99)
    print(
        f"\n[SLO] {endpoint}: "
        f"p50={p50:.0f}ms  p95={p95:.0f}ms  p99={p99:.0f}ms  "
        f"(n={len(samples_ms)})"
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def client():
    # Import here so sys.path manipulation in conftest.py has already run.
    from src.main import app  # noqa: PLC0415

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=30,
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.slow
@pytest.mark.asyncio
async def test_preview_slo_p95(client: AsyncClient) -> None:
    """SC-002: POST /api/flange/preview p95 ≤ 5 000 ms."""
    samples_ms: list[float] = []

    for _ in range(N_SAMPLES):
        t0 = time.perf_counter()
        r = await client.post("/api/flange/preview", json=VALID_SPEC)
        elapsed = (time.perf_counter() - t0) * 1000
        assert r.status_code == 200, f"Unexpected status {r.status_code}: {r.text[:200]}"
        samples_ms.append(elapsed)

    _print_stats("/api/flange/preview", samples_ms)

    p95 = _percentile(samples_ms, 95)
    assert p95 <= 5000, (
        f"SC-002 VIOLATED: /preview p95={p95:.0f}ms exceeds 5 000 ms SLO"
    )


@pytest.mark.slow
@pytest.mark.asyncio
@oda_skip
async def test_dwg_slo_p95(client: AsyncClient) -> None:
    """SC-003: POST /api/flange/dwg p95 ≤ 3 000 ms (first-byte time).

    Skipped automatically when ODA File Converter is not installed.
    """
    # Ensure ezdxf can locate the ODA binary within this subprocess.
    oda_path = os.environ.get(
        "ODAFC_EXEC_PATH",
        "/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter",
    )
    if Path(oda_path).is_file():
        os.environ["ODAFC_EXEC_PATH"] = oda_path

    samples_ms: list[float] = []

    for _ in range(N_SAMPLES):
        t0 = time.perf_counter()
        r = await client.post("/api/flange/dwg", json=VALID_SPEC)
        elapsed = (time.perf_counter() - t0) * 1000
        assert r.status_code == 200, f"Unexpected status {r.status_code}: {r.text[:200]}"
        samples_ms.append(elapsed)

    _print_stats("/api/flange/dwg", samples_ms)

    p95 = _percentile(samples_ms, 95)
    assert p95 <= 3000, (
        f"SC-003 VIOLATED: /dwg p95={p95:.0f}ms exceeds 3 000 ms SLO"
    )


@pytest.mark.slow
@pytest.mark.asyncio
async def test_pdf_slo_p95(client: AsyncClient) -> None:
    """SC-003: POST /api/flange/pdf p95 ≤ 3 000 ms."""
    samples_ms: list[float] = []

    for _ in range(N_SAMPLES):
        t0 = time.perf_counter()
        r = await client.post("/api/flange/pdf", json=VALID_SPEC)
        elapsed = (time.perf_counter() - t0) * 1000
        assert r.status_code == 200, f"Unexpected status {r.status_code}: {r.text[:200]}"
        samples_ms.append(elapsed)

    _print_stats("/api/flange/pdf", samples_ms)

    p95 = _percentile(samples_ms, 95)
    assert p95 <= 3000, (
        f"SC-003 VIOLATED: /pdf p95={p95:.0f}ms exceeds 3 000 ms SLO"
    )
