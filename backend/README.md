# Backend — Flange Generator

Python 3.11 FastAPI service generating SVG / DWG R2000 / PDF outputs from a 7-field flange specification. Stateless.

See [`../specs/001-flange-generator/quickstart.md`](../specs/001-flange-generator/quickstart.md) for full setup, including ODA File Converter installation.

## Quick start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/check_oda.sh
uvicorn src.main:app --reload --port 8000
```

Health check: `curl http://localhost:8000/api/health`
