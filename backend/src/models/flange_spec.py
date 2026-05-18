from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

DecimalMm = Annotated[float, Field(gt=0, le=100000)]


class FlangeSpecification(BaseModel):
    """7-field blower inlet flange specification.

    All mm fields accept up to 2 decimal places; values are quantized
    on input to avoid float drift surprising the user.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    inner_diameter_mm: DecimalMm
    pcd_mm: DecimalMm
    outer_diameter_mm: DecimalMm
    bolt_hole_count: Annotated[int, Field(ge=1, le=1024)]
    bolt_hole_diameter_mm: DecimalMm
    thickness_mm: DecimalMm
    material: Literal["SS400"] = "SS400"

    @model_validator(mode="after")
    def _quantize_and_validate(self) -> Self:
        for name in (
            "inner_diameter_mm",
            "pcd_mm",
            "outer_diameter_mm",
            "bolt_hole_diameter_mm",
            "thickness_mm",
        ):
            raw = getattr(self, name)
            quantized = float(Decimal(str(raw)).quantize(Decimal("0.01")))
            object.__setattr__(self, name, quantized)

        if not (self.inner_diameter_mm < self.pcd_mm < self.outer_diameter_mm):
            raise ValueError(
                "Diameters must satisfy: inner_diameter_mm < pcd_mm < outer_diameter_mm"
            )

        max_hole_outer = (self.outer_diameter_mm - self.pcd_mm) / 2
        max_hole_inner = (self.pcd_mm - self.inner_diameter_mm) / 2
        max_hole = min(max_hole_outer, max_hole_inner)
        if self.bolt_hole_diameter_mm >= max_hole:
            raise ValueError(
                "bolt_hole_diameter_mm would overlap inner or outer edge "
                f"(must be < {max_hole:.2f} mm)"
            )

        return self
