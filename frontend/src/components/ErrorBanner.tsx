"use client";

import type { ApiErrorItem } from "@/types/flange";
import { toReadableErrors } from "@/lib/error-messages";

type Props = {
  errors: ApiErrorItem[] | null;
};

export function ErrorBanner({ errors }: Props) {
  if (!errors || errors.length === 0) return null;
  const messages = toReadableErrors(errors);
  return (
    <div
      role="alert"
      className="rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700"
    >
      <p className="font-semibold mb-1">無法產生：</p>
      <ul className="list-disc pl-5 space-y-0.5">
        {messages.map((msg, idx) => (
          <li key={idx}>{msg}</li>
        ))}
      </ul>
    </div>
  );
}
