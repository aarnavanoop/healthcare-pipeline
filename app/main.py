from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.routes import patients
from app.routes import auth

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("api_engine")


limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


app = FastAPI(
    title="AI Patient Triage API",
    description="Backend engine for processing patient telemetry and RAG integration.",
    version="1.0.0"
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Catches all standard HTTP errors (401, 403, 404, etc.) and formats them cleanly."""
    logger.warning(f"HTTP Error {exc.status_code} on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "type": "http_error", "message": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Catches 422 errors (bad Pydantic data) and formats them cleanly."""
    logger.warning(f"Validation Error on {request.url.path}")
    return JSONResponse(
        status_code=422,
        content={"error": True, "type": "validation_error", "message": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches fatal 500 Internal Server Errors to prevent HTML stack traces leaking."""
    logger.error(f"FATAL 500 ERROR on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": True, "type": "internal_error", "message": "An unexpected server error occurred."},
    )

# --- Routes ---
@app.get("/health", tags=["System"])

@limiter.limit("5/second") 
async def health_check(request: Request):
    """
    Returns the system health status. 
    Used by AWS App Runner and Docker health checks.
    """
    logger.info("Health check endpoint queried.")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database_connected": "pending"
    }

app.include_router(patients.router)
app.include_router(auth.router)