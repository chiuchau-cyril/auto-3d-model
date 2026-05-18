from src.lib.layers import ALL_LAYERS
from src.models.flange_spec import FlangeSpecification
from src.services.dxf_builder import build_dxf_document


def test_dxf_version_is_r2000(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    # R2000 internal identifier is AC1015
    assert doc.dxfversion == "AC1015"


def test_units_are_millimeters(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    assert doc.header["$INSUNITS"] == 4


def test_all_required_layers_present(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    layer_names = {layer.dxf.name for layer in doc.layers}
    for spec_layer in ALL_LAYERS:
        assert spec_layer.name in layer_names


def test_outline_has_two_circles(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    msp = doc.modelspace()
    outline_circles = [
        e for e in msp.query("CIRCLE") if e.dxf.layer == "OUTLINE"
    ]
    assert len(outline_circles) == 2


def test_hole_count_matches_spec(valid_spec_kwargs):
    valid_spec_kwargs["bolt_hole_count"] = 12
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    msp = doc.modelspace()
    holes = [e for e in msp.query("CIRCLE") if e.dxf.layer == "HOLES"]
    assert len(holes) == 12


def test_watermark_text_present(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    msp = doc.modelspace()
    texts = [e.dxf.text for e in msp.query("TEXT") if e.dxf.layer == "WATERMARK"]
    assert any("Customer Preview Only" in t for t in texts)


def test_annotations_include_all_seven_fields(valid_spec_kwargs):
    spec = FlangeSpecification(**valid_spec_kwargs)
    doc = build_dxf_document(spec)
    msp = doc.modelspace()
    text_blob = " ".join(
        e.dxf.text for e in msp.query("TEXT") if e.dxf.layer in ("DIM", "ANNOTATION")
    )
    for keyword in [
        "Inner Diameter",
        "PCD",
        "Outer Diameter",
        "Bolt Hole Count",
        "Bolt Hole Diameter",
        "Thickness",
        "Material",
        "SS400",
    ]:
        assert keyword in text_blob, f"missing '{keyword}'"
