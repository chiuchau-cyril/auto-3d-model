import type { ApiErrorItem } from "@/types/flange";

const FIELD_LABELS: Record<string, string> = {
  inner_diameter_mm: "內徑",
  pcd_mm: "PCD",
  outer_diameter_mm: "外徑",
  bolt_hole_count: "孔數",
  bolt_hole_diameter_mm: "孔徑",
  thickness_mm: "厚度",
  material: "材質",
  server: "系統",
  body: "輸入內容",
};

const MESSAGE_HINTS: Array<[RegExp, string]> = [
  // Geometry / cross-field validation (model_validator)
  [/must be greater than inner diameter/i, "PCD 必須大於內徑"],
  [/Diameters must satisfy/i, "尺寸必須滿足：內徑 < PCD < 外徑"],
  [/overlap inner or outer edge/i, "孔徑會壓到內或外緣"],
  // Material
  [/Only SS400 is supported/i, "v1 僅支援材質 SS400"],
  [/Input should be 'SS400'/i, "v1 僅支援材質 SS400"],
  // Required / missing fields
  [/Field required/i, "此欄位為必填"],
  // Numeric range errors (Pydantic v2 messages)
  [/Input should be greater than 0/i, "必須大於 0"],
  [/Input should be greater than or equal to 1/i, "孔數至少 1 個"],
  [/Input should be less than or equal to 1024/i, "孔數不可超過 1024"],
  [/Input should be less than or equal to 100000/i, "數值超過上限（100 000 mm）"],
  // Extra / unknown fields
  [/Extra inputs are not permitted/i, "包含不允許的欄位"],
  // DWG export runtime failure
  [/DWG export failed/i, "DWG 產生失敗，請重試"],
  // ODA converter availability
  [/ODA File Converter is not installed/i, "後端缺少 ODA File Converter，無法產生 DWG"],
  // Legacy / decimal precision (kept for backwards compat)
  [/decimal_places/i, "最多 2 位小數"],
];

export function toReadableErrors(errors: ApiErrorItem[]): string[] {
  return errors.map((err) => {
    const label = FIELD_LABELS[err.field] ?? err.field;
    const hint = MESSAGE_HINTS.find(([re]) => re.test(err.message))?.[1];
    return hint ? `${label}：${hint}` : `${label}：${err.message}`;
  });
}
