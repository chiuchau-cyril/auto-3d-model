import type {
  ApiErrorResponse,
  FlangeSpec,
  HealthResponse,
} from "@/types/flange";

const BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  errors: ApiErrorResponse["errors"];
  constructor(status: number, errors: ApiErrorResponse["errors"]) {
    super(errors.map((e) => `${e.field}: ${e.message}`).join("; "));
    this.status = status;
    this.errors = errors;
  }
}

async function postJson(path: string, spec: FlangeSpec): Promise<Response> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(spec),
  });
  if (!res.ok) {
    let payload: ApiErrorResponse;
    try {
      payload = (await res.json()) as ApiErrorResponse;
    } catch {
      payload = { errors: [{ field: "server", message: res.statusText }] };
    }
    throw new ApiError(res.status, payload.errors);
  }
  return res;
}

export async function fetchPreviewSvg(spec: FlangeSpec): Promise<string> {
  const res = await postJson("/api/flange/preview", spec);
  return res.text();
}

export async function downloadDwg(spec: FlangeSpec): Promise<Blob> {
  const res = await postJson("/api/flange/dwg", spec);
  return res.blob();
}

export async function downloadPdf(spec: FlangeSpec): Promise<Blob> {
  const res = await postJson("/api/flange/pdf", spec);
  return res.blob();
}

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BASE}/api/health`);
  if (!res.ok) {
    throw new ApiError(res.status, [{ field: "server", message: res.statusText }]);
  }
  return res.json() as Promise<HealthResponse>;
}

export function filenameFromContentDisposition(header: string | null): string | null {
  if (!header) return null;
  const match = /filename="?([^";]+)"?/.exec(header);
  return match?.[1] ?? null;
}
