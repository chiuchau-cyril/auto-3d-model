# Frontend — Flange Generator

Next.js 15 (App Router) UI. Traditional Chinese interface; generates English-annotated SVG/DWG/PDF via the backend.

See [`../specs/001-flange-generator/quickstart.md`](../specs/001-flange-generator/quickstart.md) for full setup.

## Quick start

```bash
pnpm install   # or: npm install
cp .env.local.example .env.local
pnpm dev       # http://localhost:3000
```

Backend must be running at `NEXT_PUBLIC_API_BASE` (default `http://localhost:8000`).
