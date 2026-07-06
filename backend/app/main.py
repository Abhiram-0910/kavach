from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models.responses import ErrorResponse, HealthResponse
from app.routers.classify import load_audio_classifier, load_image_classifier, router as classify_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ponytail: sync model loads block event loop briefly on startup — fine for demo;
    # wrap in run_in_executor if startup latency becomes a problem in production.
    load_image_classifier()
    load_audio_classifier()
    yield


app = FastAPI(title="Kavach API", version="0.1.0", lifespan=lifespan)

app.include_router(classify_router)


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
    return _error_response(422, "Validation error", exc.errors())


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
