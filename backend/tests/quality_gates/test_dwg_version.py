"""Quality Gate — DWG version must be AC1015 (R2000).

DWG is a proprietary binary format; ezdxf.readfile() reads DXF, not DWG.
Version is determined by reading the 6-byte magic at the start of the file.
AC1015 is the R2000 version identifier embedded in the binary DWG header.
"""

import pytest

from tests.conftest import oda_skip
from src.models.flange_spec import FlangeSpecification
from src.services.dxf_builder import build_dxf_document
from src.services.dwg_exporter import export_dwg


@oda_skip
def test_dwg_dxfversion_is_ac1015(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    dwg_bytes = export_dwg(doc)
    # DWG R2000 begins with the 6-byte ASCII version string "AC1015"
    assert dwg_bytes[:6] == b"AC1015"
