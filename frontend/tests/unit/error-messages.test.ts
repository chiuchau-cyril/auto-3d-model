/**
 * Unit tests for toReadableErrors — T059.
 *
 * Verifies that every backend error string is mapped to the expected
 * Traditional Chinese hint, and that FIELD_LABELS covers all 7 Pydantic
 * field names plus the virtual "server" / "body" keys.
 */
import { describe, expect, it } from "vitest";
import { toReadableErrors } from "@/lib/error-messages";
import type { ApiErrorItem } from "@/types/flange";

function err(field: string, message: string): ApiErrorItem {
  return { field, message };
}

describe("toReadableErrors — geometry / cross-field errors", () => {
  it("maps Diameters must satisfy to Chinese hint", () => {
    const result = toReadableErrors([
      err(
        "body",
        "Diameters must satisfy: inner_diameter_mm < pcd_mm < outer_diameter_mm",
      ),
    ]);
    expect(result[0]).toBe("輸入內容：尺寸必須滿足：內徑 < PCD < 外徑");
  });

  it("maps overlap inner or outer edge to Chinese hint", () => {
    const result = toReadableErrors([
      err(
        "bolt_hole_diameter_mm",
        "bolt_hole_diameter_mm would overlap inner or outer edge (must be < 25.00 mm)",
      ),
    ]);
    expect(result[0]).toBe("孔徑：孔徑會壓到內或外緣");
  });
});

describe("toReadableErrors — field-level Pydantic errors", () => {
  it("maps Field required to 此欄位為必填", () => {
    const result = toReadableErrors([
      err("inner_diameter_mm", "Field required"),
    ]);
    expect(result[0]).toBe("內徑：此欄位為必填");
  });

  it("maps Input should be greater than 0 to 必須大於 0", () => {
    const result = toReadableErrors([
      err("thickness_mm", "Input should be greater than 0"),
    ]);
    expect(result[0]).toBe("厚度：必須大於 0");
  });

  it("maps bolt_hole_count too small to 孔數至少 1 個", () => {
    const result = toReadableErrors([
      err("bolt_hole_count", "Input should be greater than or equal to 1"),
    ]);
    expect(result[0]).toBe("孔數：孔數至少 1 個");
  });

  it("maps bolt_hole_count too large to 孔數不可超過 1024", () => {
    const result = toReadableErrors([
      err("bolt_hole_count", "Input should be less than or equal to 1024"),
    ]);
    expect(result[0]).toBe("孔數：孔數不可超過 1024");
  });

  it("maps mm value too large to over-limit message", () => {
    const result = toReadableErrors([
      err(
        "outer_diameter_mm",
        "Input should be less than or equal to 100000",
      ),
    ]);
    expect(result[0]).toBe("外徑：數值超過上限（100 000 mm）");
  });

  it("maps Input should be 'SS400' to material hint", () => {
    const result = toReadableErrors([
      err("material", "Input should be 'SS400'"),
    ]);
    expect(result[0]).toBe("材質：v1 僅支援材質 SS400");
  });

  it("maps Extra inputs are not permitted to Chinese hint", () => {
    const result = toReadableErrors([
      err("foo", "Extra inputs are not permitted"),
    ]);
    // Unknown field "foo" is kept as-is; hint is still applied.
    expect(result[0]).toBe("foo：包含不允許的欄位");
  });
});

describe("toReadableErrors — server / ODA errors", () => {
  it("maps ODA File Converter is not installed to Chinese hint", () => {
    const result = toReadableErrors([
      err(
        "server",
        "ODA File Converter is not installed or ODAFC_EXEC_PATH is invalid",
      ),
    ]);
    expect(result[0]).toBe("系統：後端缺少 ODA File Converter，無法產生 DWG");
  });

  it("maps DWG export failed to retry hint", () => {
    const result = toReadableErrors([
      err("server", "DWG export failed: some underlying error"),
    ]);
    expect(result[0]).toBe("系統：DWG 產生失敗，請重試");
  });
});

describe("toReadableErrors — fallback for unrecognised messages", () => {
  it("passes through raw English message when no hint matches", () => {
    const result = toReadableErrors([
      err("pcd_mm", "some unexpected backend error"),
    ]);
    expect(result[0]).toBe("PCD：some unexpected backend error");
  });

  it("uses field name as label when field is unknown", () => {
    const result = toReadableErrors([
      err("unknown_field", "Field required"),
    ]);
    expect(result[0]).toBe("unknown_field：此欄位為必填");
  });
});

describe("toReadableErrors — handles multiple errors in one call", () => {
  it("maps an array of mixed errors to correct TC hints", () => {
    const result = toReadableErrors([
      err("inner_diameter_mm", "Field required"),
      err("pcd_mm", "Input should be greater than 0"),
      err(
        "body",
        "Diameters must satisfy: inner_diameter_mm < pcd_mm < outer_diameter_mm",
      ),
    ]);
    expect(result).toHaveLength(3);
    expect(result[0]).toBe("內徑：此欄位為必填");
    expect(result[1]).toBe("PCD：必須大於 0");
    expect(result[2]).toBe("輸入內容：尺寸必須滿足：內徑 < PCD < 外徑");
  });
});
