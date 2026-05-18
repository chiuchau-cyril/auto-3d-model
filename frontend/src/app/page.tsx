"use client";

import { useState } from "react";
import { ApiError, fetchPreviewSvg } from "@/lib/api";
import { ErrorBanner } from "@/components/ErrorBanner";
import { FlangeForm } from "@/components/FlangeForm";
import { PreviewPane } from "@/components/PreviewPane";
import type { ApiErrorItem, FlangeSpec } from "@/types/flange";

export default function HomePage() {
  const [svg, setSvg] = useState<string | null>(null);
  const [spec, setSpec] = useState<FlangeSpec | null>(null);
  const [errors, setErrors] = useState<ApiErrorItem[] | null>(null);
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (next: FlangeSpec) => {
    setBusy(true);
    setErrors(null);
    try {
      const result = await fetchPreviewSvg(next);
      setSvg(result);
      setSpec(next);
    } catch (err) {
      setSvg(null);
      if (err instanceof ApiError) setErrors(err.errors);
      else setErrors([{ field: "server", message: String(err) }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-4 p-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-xl font-semibold text-slate-900">
          鼓風機入口法蘭產生器
        </h1>
        <div
          role="note"
          className="rounded border border-amber-300 bg-amber-50 px-3 py-1.5 text-sm font-medium text-amber-800"
        >
          For Customer Preview Only — Not for Manufacturing
        </div>
      </header>

      <div className="grid flex-1 gap-4 md:grid-cols-[360px_1fr]">
        <aside className="rounded-lg border border-slate-200 bg-white p-4">
          <FlangeForm onSubmit={handleSubmit} busy={busy} />
          <div className="mt-4">
            <ErrorBanner errors={errors} />
          </div>
        </aside>

        <PreviewPane
          svg={svg}
          spec={spec}
          loading={busy}
          onDownloadError={(err) => setErrors(err.errors)}
        />
      </div>
    </main>
  );
}
