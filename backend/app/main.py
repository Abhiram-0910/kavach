from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models.responses import ErrorResponse, HealthResponse
from app.routers.classify import load_audio_classifier, load_image_classifier, router as classify_router
from app.routers.document import load_vision_client, router as document_router
from app.routers.honeypot import router as honeypot_router
from app.routers.complaint import router as complaint_router
from app.routers.digital_arrest import router as digital_arrest_router
from app.routers.vault import router as vault_router
from app.routers.phishing import load_phishing_blocklist, router as phishing_router
from app.routers.social_profile import router as social_profile_router
from app.services.honeypot_pipeline import load_tts_client, load_whisper_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ponytail: sync loads block briefly at startup — fine for demo
    load_image_classifier()
    load_audio_classifier()
    load_vision_client()
    load_whisper_model()
    load_tts_client()
    load_phishing_blocklist()
    yield


app = FastAPI(title="Kavach API", version="0.1.0", lifespan=lifespan)

app.include_router(classify_router)
app.include_router(document_router)
app.include_router(honeypot_router)
app.include_router(phishing_router)
app.include_router(social_profile_router)
app.include_router(complaint_router)
app.include_router(digital_arrest_router)
app.include_router(vault_router)


def _error_response(status_code: int, error: str, detail: Any = None) -> JSONResponse:
    """Build a guaranteed-JSON error response. Every error in this codebase flows through here."""
    content: dict[str, Any] = {"error": error, "status_code": status_code}
    if detail is not None:
        content["detail"] = detail
    return JSONResponse(status_code=status_code, content=content)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return _error_response(exc.status_code, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Pydantic v2 model_validator errors include a ValueError object in ctx["error"],
    # which json.dumps cannot serialize. Convert to str to keep the response valid JSON.
    errors = exc.errors()
    for err in errors:
        ctx = err.get("ctx", {})
        if isinstance(ctx.get("error"), Exception):
            ctx["error"] = str(ctx["error"])
    return _error_response(422, "Validation error", errors)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return _error_response(500, "Internal server error", str(exc))


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness check."""
    return HealthResponse(status="ok")


# ponytail: test-only route — gate behind DEBUG env var before production
@app.get("/debug/crash", response_model=ErrorResponse)
async def crash() -> None:
    """Intentionally raises to verify the global exception handler returns JSON."""
    raise RuntimeError("Intentional crash for testing")
