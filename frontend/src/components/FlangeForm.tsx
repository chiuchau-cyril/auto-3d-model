"use client";

import { useMemo, useState } from "react";
import { flangeSpecSchema, type FlangeSpec } from "@/lib/schema";

const FIELDS: Array<{
  key: keyof Omit<FlangeSpec, "material">;
  label: string;
  step: string;
  integer?: boolean;
}> = [
  { key: "inner_diameter_mm", label: "內徑", step: "0.01" },
  { key: "pcd_mm", label: "PCD", step: "0.01" },
  { key: "outer_diameter_mm", label: "外徑", step: "0.01" },
  { key: "bolt_hole_count", label: "孔數", step: "1", integer: true },
  { key: "bolt_hole_diameter_mm", label: "孔徑", step: "0.01" },
  { key: "thickness_mm", label: "厚度", step: "0.01" },
];

type Props = {
  onSubmit: (spec: FlangeSpec) => void;
  busy?: boolean;
};

type Inputs = Record<string, string>;

export function FlangeForm({ onSubmit, busy }: Props) {
  const [inputs, setInputs] = useState<Inputs>({});

  const parsed = useMemo(() => {
    const numeric = Object.fromEntries(
      FIELDS.map((f) => {
        const raw = inputs[f.key] ?? "";
        if (raw === "") return [f.key, undefined];
        const n = Number(raw);
        return [f.key, Number.isFinite(n) ? n : undefined];
      })
    );
    if (Object.values(numeric).some((v) => v === undefined)) {
      return { ok: false as const, errors: {} as Record<string, string> };
    }
    const result = flangeSpecSchema.safeParse({ ...numeric, material: "SS400" });
    if (result.success) return { ok: true as const, data: result.data };
    const errors: Record<string, string> = {};
    for (const issue of result.error.issues) {
      const key = issue.path[0]?.toString() ?? "form";
      if (!errors[key]) errors[key] = issue.message;
    }
    return { ok: false as const, errors };
  }, [inputs]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (parsed.ok) onSubmit(parsed.data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <fieldset className="space-y-3">
        <legend className="text-sm font-semibold text-slate-700">
          尺寸（單位：mm）
        </legend>
        {FIELDS.map((f) => {
          const err = !parsed.ok ? parsed.errors[f.key] : undefined;
          return (
            <label key={f.key} className="block text-sm">
              <span className="block text-slate-700">{f.label}</span>
              <input
                type="number"
                step={f.step}
                inputMode={f.integer ? "numeric" : "decimal"}
                value={inputs[f.key] ?? ""}
                onChange={(e) =>
                  setInputs((prev) => ({ ...prev, [f.key]: e.target.value }))
                }
                className="mt-1 block w-full rounded border border-slate-300 px-2 py-1.5 focus:border-slate-500 focus:outline-none"
                aria-invalid={Boolean(err)}
                data-testid={`field-${f.key}`}
              />
              {err && (
                <span
                  className="mt-1 block text-xs text-red-600"
                  data-testid={`error-${f.key}`}
                >
                  {err}
                </span>
              )}
            </label>
          );
        })}
        <label className="block text-sm">
          <span className="block text-slate-700">材質</span>
          <input
            type="text"
            value="SS400"
            disabled
            data-testid="field-material"
            className="mt-1 block w-full rounded border border-slate-200 bg-slate-100 px-2 py-1.5 text-slate-500"
          />
        </label>
      </fieldset>

      <button
        type="submit"
        disabled={!parsed.ok || busy}
        data-testid="submit"
        className="w-full rounded bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {busy ? "產生中…" : "產生"}
      </button>
    </form>
  );
}
