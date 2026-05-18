"use client";

import type { FlangeSpec } from "@/types/flange";
import {
  downloadDwg,
  downloadPdf,
  filenameFromContentDisposition,
  ApiError,
} from "@/lib/api";
import { triggerDownload } from "@/lib/download";
import { useState } from "react";

type Props = {
  svg: string | null;
  spec: FlangeSpec | null;
  loading?: boolean;
  onDownloadError: (err: ApiError) => void;
};

async function downloadWith(
  fn: (spec: FlangeSpec) => Promise<Blob>,
  spec: FlangeSpec,
  ext: "dwg" | "pdf"
): Promise<void> {
  const blob = await fn(spec);
  // Re-fetch to get Content-Disposition header (api wrapper drops it for now).
  const fallback = `flange_${spec.inner_diameter_mm}x${spec.outer_diameter_mm}_PCD${spec.pcd_mm}_${spec.bolt_hole_count}H_${spec.thickness_mm}t.${ext}`;
  triggerDownload(blob, fallback);
}

export function PreviewPane({ svg, spec, loading, onDownloadError }: Props) {
  const [busy, setBusy] = useState<null | "dwg" | "pdf">(null);
  const handle = (kind: "dwg" | "pdf") => async () => {
    if (!spec) return;
    setBusy(kind);
    try {
      await downloadWith(kind === "dwg" ? downloadDwg : downloadPdf, spec, kind);
    } catch (err) {
      if (err instanceof ApiError) onDownloadError(err);
    } finally {
      setBusy(null);
    }
  };

  return (
    <section className="flex h-full flex-col gap-3">
      <header className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-700">預覽</h2>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handle("dwg")}
            disabled={!svg || !spec || busy !== null}
            data-testid="download-dwg"
            className="rounded border border-slate-300 px-3 py-1.5 text-xs hover:bg-slate-100 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
          >
            {busy === "dwg" ? "下載中…" : "下載 DWG"}
          </button>
          <button
            type="button"
            onClick={handle("pdf")}
            disabled={!svg || !spec || busy !== null}
            data-testid="download-pdf"
            className="rounded border border-slate-300 px-3 py-1.5 text-xs hover:bg-slate-100 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
          >
            {busy === "pdf" ? "下載中…" : "下載 PDF"}
          </button>
        </div>
      </header>
      <div
        className="flex flex-1 items-center justify-center rounded border border-dashed border-slate-300 bg-white p-4"
        data-testid="preview-container"
      >
        {loading && <p className="text-sm text-slate-500">產生中…</p>}
        {!loading && !svg && (
          <p className="text-sm text-slate-400">輸入規格並按「產生」</p>
        )}
        {!loading && svg && (
          <div
            className="max-h-full max-w-full"
            data-testid="preview-svg"
            dangerouslySetInnerHTML={{ __html: svg }}
          />
        )}
      </div>
    </section>
  );
}
