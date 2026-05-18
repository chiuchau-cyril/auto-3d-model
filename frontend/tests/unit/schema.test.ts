import { describe, it, expect } from "vitest";
import { flangeSpecSchema } from "@/lib/schema";

const VALID = {
  inner_diameter_mm: 100,
  pcd_mm: 150,
  outer_diameter_mm: 200,
  bolt_hole_count: 4,
  bolt_hole_diameter_mm: 10,
  thickness_mm: 12,
  material: "SS400" as const,
};

describe("flangeSpecSchema", () => {
  it("accepts a valid spec", () => {
    const result = flangeSpecSchema.safeParse(VALID);
    expect(result.success).toBe(true);
  });

  it("fails when inner_diameter_mm is missing", () => {
    const { inner_diameter_mm: _, ...rest } = VALID;
    const result = flangeSpecSchema.safeParse(rest);
    expect(result.success).toBe(false);
    if (!result.success) {
      const paths = result.error.issues.map((i) => i.path[0]);
      expect(paths).toContain("inner_diameter_mm");
    }
  });

  it("fails when a field is zero", () => {
    const result = flangeSpecSchema.safeParse({ ...VALID, inner_diameter_mm: 0 });
    expect(result.success).toBe(false);
    if (!result.success) {
      const msgs = result.error.issues.map((i) => i.message);
      expect(msgs.some((m) => m.includes("必須大於 0"))).toBe(true);
    }
  });

  it("fails when a field is negative", () => {
    const result = flangeSpecSchema.safeParse({ ...VALID, thickness_mm: -1 });
    expect(result.success).toBe(false);
    if (!result.success) {
      const msgs = result.error.issues.map((i) => i.message);
      expect(msgs.some((m) => m.includes("必須大於 0"))).toBe(true);
    }
  });

  it("fails when a dimension has more than 2 decimal places", () => {
    const result = flangeSpecSchema.safeParse({ ...VALID, thickness_mm: 12.123 });
    expect(result.success).toBe(false);
    if (!result.success) {
      const msgs = result.error.issues.map((i) => i.message);
      expect(msgs).toContain("最多 2 位小數");
    }
  });

  it("fails when pcd_mm <= inner_diameter_mm", () => {
    const result = flangeSpecSchema.safeParse({ ...VALID, pcd_mm: 100 });
    expect(result.success).toBe(false);
    if (!result.success) {
      const issue = result.error.issues.find((i) => i.path[0] === "pcd_mm");
      expect(issue?.message).toBe("PCD 必須大於內徑");
    }
  });

  it("fails when pcd_mm is less than inner_diameter_mm", () => {
    const result = flangeSpecSchema.safeParse({ ...VALID, pcd_mm: 90 });
    expect(result.success).toBe(false);
    if (!result.success) {
      const issue = result.error.issues.find((i) => i.path[0] === "pcd_mm");
      expect(issue?.message).toBe("PCD 必須大於內徑");
    }
  });

  it("fails when outer_diameter_mm <= pcd_mm", () => {
    const result = flangeSpecSchema.safeParse({ ...VALID, outer_diameter_mm: 150 });
    expect(result.success).toBe(false);
    if (!result.success) {
      const issue = result.error.issues.find((i) => i.path[0] === "outer_diameter_mm");
      expect(issue?.message).toBe("外徑必須大於 PCD");
    }
  });

  it("fails when outer_diameter_mm is less than pcd_mm", () => {
    const result = flangeSpecSchema.safeParse({ ...VALID, outer_diameter_mm: 140 });
    expect(result.success).toBe(false);
    if (!result.success) {
      const issue = result.error.issues.find((i) => i.path[0] === "outer_diameter_mm");
      expect(issue?.message).toBe("外徑必須大於 PCD");
    }
  });

  it("fails when bolt_hole_diameter_mm causes overflow into flanges", () => {
    // maxOuter = (200-150)/2 = 25, maxInner = (150-100)/2 = 25, maxHole = 25
    // bolt_hole_diameter_mm must be < 25
    const result = flangeSpecSchema.safeParse({ ...VALID, bolt_hole_diameter_mm: 25 });
    expect(result.success).toBe(false);
    if (!result.success) {
      const issue = result.error.issues.find((i) => i.path[0] === "bolt_hole_diameter_mm");
      expect(issue?.message).toContain("孔徑會壓到內或外緣");
    }
  });

  it("fails when material is not SS400", () => {
    const result = flangeSpecSchema.safeParse({ ...VALID, material: "A36" });
    expect(result.success).toBe(false);
    if (!result.success) {
      const paths = result.error.issues.map((i) => i.path[0]);
      expect(paths).toContain("material");
    }
  });

  it("fails when bolt_hole_count is not an integer", () => {
    const result = flangeSpecSchema.safeParse({ ...VALID, bolt_hole_count: 4.5 });
    expect(result.success).toBe(false);
    if (!result.success) {
      const msgs = result.error.issues.map((i) => i.message);
      expect(msgs).toContain("必須是整數");
    }
  });

  it("fails when bolt_hole_count is less than 1", () => {
    const result = flangeSpecSchema.safeParse({ ...VALID, bolt_hole_count: 0 });
    expect(result.success).toBe(false);
    if (!result.success) {
      const msgs = result.error.issues.map((i) => i.message);
      expect(msgs.some((m) => m.includes("至少 1 個孔"))).toBe(true);
    }
  });
});
