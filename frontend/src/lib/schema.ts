import { z } from "zod";

const positiveMm = z
  .number({ invalid_type_error: "請輸入數字" })
  .positive("必須大於 0")
  .max(100000, "數值過大")
  .refine(
    (n) => Math.round(n * 100) === n * 100,
    { message: "最多 2 位小數" }
  );

export const flangeSpecSchema = z
  .object({
    inner_diameter_mm: positiveMm,
    pcd_mm: positiveMm,
    outer_diameter_mm: positiveMm,
    bolt_hole_count: z
      .number({ invalid_type_error: "請輸入整數" })
      .int("必須是整數")
      .min(1, "至少 1 個孔")
      .max(1024, "孔數過多"),
    bolt_hole_diameter_mm: positiveMm,
    thickness_mm: positiveMm,
    material: z.literal("SS400"),
  })
  .superRefine((spec, ctx) => {
    if (!(spec.inner_diameter_mm < spec.pcd_mm)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["pcd_mm"],
        message: "PCD 必須大於內徑",
      });
    }
    if (!(spec.pcd_mm < spec.outer_diameter_mm)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["outer_diameter_mm"],
        message: "外徑必須大於 PCD",
      });
    }
    const maxOuter = (spec.outer_diameter_mm - spec.pcd_mm) / 2;
    const maxInner = (spec.pcd_mm - spec.inner_diameter_mm) / 2;
    const maxHole = Math.min(maxOuter, maxInner);
    if (spec.bolt_hole_diameter_mm >= maxHole) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["bolt_hole_diameter_mm"],
        message: `孔徑會壓到內或外緣（必須 < ${maxHole.toFixed(2)} mm）`,
      });
    }
  });

export type FlangeSpec = z.infer<typeof flangeSpecSchema>;
