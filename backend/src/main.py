from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from src.api.responses import validation_error_response

app = FastAPI(
    title="Flange Generator API",
    version="1.0.0",
    description="Stateless API to generate SVG/DWG/PDF previews of blower inlet flanges.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def on_validation_error(_: Request, exc: RequestValidationError):
    items: list[tuple[str, str]] = []
    for err in exc.errors():
        loc = err.get("loc", [])
        field = ".".join(str(p) for p in loc[1:]) if len(loc) > 1 else (loc[0] if loc else "body")
        message = err.get("msg", "invalid value")
        if isinstance(message, str) and message.startswith("Value error, "):
            message = message[len("Value error, "):]
        items.append((str(field), message))
    return validation_error_response(items)


# Routes are registered in src/api/routes.py via include_router (T032)
from src.api.routes import router as flange_router  # noqa: E402

app.include_router(flange_router)
