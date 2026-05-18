"""Shared pytest fixtures."""

import os
import sys
from pathlib import Path

import pytest

# Ensure backend/ is on sys.path so `import src.xxx` works regardless of CWD.
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def valid_spec_kwargs() -> dict:
    return {
        "inner_diameter_mm": 100.0,
        "pcd_mm": 150.0,
        "outer_diameter_mm": 200.0,
        "bolt_hole_count": 8,
        "bolt_hole_diameter_mm": 12.0,
        "thickness_mm": 20.0,
        "material": "SS400",
    }


def requires_oda() -> bool:
    explicit = os.environ.get("ODAFC_EXEC_PATH")
    if explicit and Path(explicit).is_file():
        return True
    default = Path("/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter")
    return default.is_file()


oda_skip = pytest.mark.skipif(
    not requires_oda(),
    reason="ODA File Converter not installed; set ODAFC_EXEC_PATH",
)
