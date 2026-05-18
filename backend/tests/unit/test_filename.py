from datetime import datetime

from src.lib.filename import build_filename
from src.models.flange_spec import FlangeSpecification


def test_integer_values_no_decimal_point(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    name = build_filename(spec, "dwg", now=datetime(2026, 5, 18, 14, 30, 22))
    assert name == "flange_100x200_PCD150_8H_20t_20260518T143022.dwg"


def test_decimal_values_trimmed(valid_spec_kwargs):
    valid_spec_kwargs["thickness_mm"] = 20.5
    spec = FlangeSpecification(**valid_spec_kwargs)
    name = build_filename(spec, "pdf", now=datetime(2026, 1, 2, 3, 4, 5))
    assert "20.5t" in name
    assert name.endswith("20260102T030405.pdf")


def test_strip_dot_in_extension(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    name = build_filename(spec, ".dwg", now=datetime(2026, 5, 18, 0, 0, 0))
    assert name.endswith(".dwg")
    assert ".." not in name
