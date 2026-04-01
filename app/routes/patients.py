from fastapi import APIRouter, Depends
import logging
from app.db.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Patient
import asyncio


logger = logging.getLogger("api_engine.patients")

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

@router.get("/")
async def get_patients(db: AsyncSession = Depends(get_db)):
    """
    Returns a paginated list of patients
    """

    logger.info("Fetched patient list")
    stmt = select(Patient).limit(10)
    result = await db.execute(stmt)
    patients = result.scalars().all()
    return patients