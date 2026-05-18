import pytest
from pydantic import ValidationError

from src.models.flange_spec import FlangeSpecification


def test_accepts_valid_spec(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    assert spec.inner_diameter_mm == 100.0
    assert spec.material == "SS400"


def test_rejects_pcd_not_between_inner_and_outer(valid_spec_kwargs):
    valid_spec_kwargs["pcd_mm"] = 100.0  # equal to inner
    with pytest.raises(ValidationError) as exc:
        FlangeSpecification(**valid_spec_kwargs)
    assert "Diameters must satisfy" in str(exc.value)


def test_rejects_bolt_hole_overlap(valid_spec_kwargs):
    valid_spec_kwargs["bolt_hole_diameter_mm"] = 30.0  # larger than (200-150)/2 = 25
    with pytest.raises(ValidationError) as exc:
        FlangeSpecification(**valid_spec_kwargs)
    assert "overlap" in str(exc.value)


def test_rejects_non_ss400_material(valid_spec_kwargs):
    valid_spec_kwargs["material"] = "SUS304"
    with pytest.raises(ValidationError):
        FlangeSpecification(**valid_spec_kwargs)


def test_default_material_is_ss400(valid_spec_kwargs):
    valid_spec_kwargs.pop("material")
    spec = FlangeSpecification(**valid_spec_kwargs)
    assert spec.material == "SS400"


def test_quantizes_to_two_decimals(valid_spec_kwargs):
    valid_spec_kwargs["thickness_mm"] = 20.1234
    spec = FlangeSpecification(**valid_spec_kwargs)
    assert spec.thickness_mm == 20.12


def test_rejects_zero_or_negative(valid_spec_kwargs):
    valid_spec_kwargs["inner_diameter_mm"] = 0
    with pytest.raises(ValidationError):
        FlangeSpecification(**valid_spec_kwargs)


def test_rejects_zero_bolt_count(valid_spec_kwargs):
    valid_spec_kwargs["bolt_hole_count"] = 0
    with pytest.raises(ValidationError):
        FlangeSpecification(**valid_spec_kwargs)


def test_rejects_extra_fields(valid_spec_kwargs):
    valid_spec_kwargs["finish"] = "polished"
    with pytest.raises(ValidationError):
        FlangeSpecification(**valid_spec_kwargs)
