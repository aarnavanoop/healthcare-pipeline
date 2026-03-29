from fastapi import FastAPI
import logging
from datetime import datetime
from app.routes import patients
from app.routes import auth


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("api_engine")

app = FastAPI(
    title="AI Patient Triage API",
    description="Backend engine for processing patient telemetry and RAG integration.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the AI Patient Triage Engine...")

@app.get("/health", tags=["System"])
async def health_check():
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