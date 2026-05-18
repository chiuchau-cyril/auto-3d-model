"""API routes for flange generation.

Endpoints (all stateless, JSON body, immediate response):
    POST /api/flange/preview  -> image/svg+xml
    POST /api/flange/dwg      -> application/acad
    POST /api/flange/pdf      -> application/pdf
    GET  /api/health          -> JSON
"""

import os

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from src.api.responses import internal_error_response, oda_unavailable_response
from src.lib.filename import build_filename
from src.models.flange_spec import FlangeSpecification
from src.services.dwg_exporter import OdaConverterNotInstalled, export_dwg
from src.services.dxf_builder import build_dxf_document
from src.services.pdf_renderer import render_pdf
from src.services.svg_renderer import render_svg

router = APIRouter()


def _oda_available() -> bool:
    path = os.environ.get("ODAFC_EXEC_PATH")
    if not path:
        # Fall back to macOS default location used by the project quickstart.
        default = "/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter"
        return os.access(default, os.X_OK)
    return os.access(path, os.X_OK)


@router.get("/api/health")
async def health() -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "oda_converter_available": _oda_available(),
            "version": "1.0.0",
        }
    )


@router.post("/api/flange/preview")
async def preview(spec: FlangeSpecification) -> Response:
    doc = build_dxf_document(spec)
    svg = render_svg(doc)
    return Response(content=svg, media_type="image/svg+xml")


@router.post("/api/flange/dwg")
async def dwg(spec: FlangeSpecification) -> Response:
    doc = build_dxf_document(spec)
    try:
        payload = export_dwg(doc)
    except OdaConverterNotInstalled:
        return oda_unavailable_response()
    except Exception as exc:  # noqa: BLE001
        return internal_error_response(f"DWG export failed: {exc}")

    filename = build_filename(spec, "dwg")
    return Response(
        content=payload,
        media_type="application/acad",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/api/flange/pdf")
async def pdf(spec: FlangeSpecification) -> Response:
    doc = build_dxf_document(spec)
    svg = render_svg(doc)
    payload = render_pdf(spec, svg)
    filename = build_filename(spec, "pdf")
    return Response(
        content=payload,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
