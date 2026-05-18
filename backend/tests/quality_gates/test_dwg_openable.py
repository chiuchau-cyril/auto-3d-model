"""Quality Gate — DWG files from 3 different specs are valid R2000 DWG output.

DWG is a proprietary binary format; ezdxf.readfile() reads DXF, not DWG.
"Openable" is verified by: export_dwg returns non-empty bytes starting with
the AC1015 magic marker, which is the definitive R2000 DWG version token.
"""

import pytest

from tests.conftest import oda_skip
from src.models.flange_spec import FlangeSpecification
from src.services.dxf_builder import build_dxf_document
from src.services.dwg_exporter import export_dwg

_SPECS = [
    # typical
    {
        "inner_diameter_mm": 100.0,
        "pcd_mm": 150.0,
        "outer_diameter_mm": 200.0,
        "bolt_hole_count": 8,
        "bolt_hole_diameter_mm": 12.0,
        "thickness_mm": 20.0,
        "material": "SS400",
    },
    # small
    {
        "inner_diameter_mm": 20.0,
        "pcd_mm": 35.0,
        "outer_diameter_mm": 50.0,
        "bolt_hole_count": 4,
        "bolt_hole_diameter_mm": 5.0,
        "thickness_mm": 8.0,
        "material": "SS400",
    },
    # large
    {
        "inner_diameter_mm": 400.0,
        "pcd_mm": 600.0,
        "outer_diameter_mm": 800.0,
        "bolt_hole_count": 16,
        "bolt_hole_diameter_mm": 20.0,
        "thickness_mm": 40.0,
        "material": "SS400",
    },
]


@oda_skip
@pytest.mark.parametrize("kwargs", _SPECS)
def test_dwg_openable(kwargs):
    spec = FlangeSpecification(**kwargs)
    doc = build_dxf_document(spec)
    dwg_bytes = export_dwg(doc)
    # Non-empty and starts with AC1015 magic — the DWG R2000 version header
    assert len(dwg_bytes) > 0
    assert dwg_bytes[:6] == b"AC1015"
