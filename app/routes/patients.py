from fastapi import APIRouter
import logging

logger = logging.getLogger("api_engine.patients")

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

@router.get("/")
async def get_patients():
    """
    Returns a paginated list of patients (Dummy endpoint)
    """

    logger.info("Fetched patient list")
    return{"message": "This will be a paginated list of patients"}