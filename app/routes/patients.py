from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
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
async def get_patients(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description = "Page number (starts at 1)"),
    size: int = Query(10, ge=1, le=100, description= "Number of records per page"),
    anomaly_flag: Optional[bool] = Query(None, description="Filter by anomaly presence"),
    ):
    """
    Returns a paginated list of patients
    """

    logger.info(f"Fetching patient list -> page: {page}, size: {size}")

    stmt = select(Patient)
    if anomaly_flag is not None:
        stmt = stmt.where(Patient.anomaly_flag == anomaly_flag)

    offset_value = (page - 1) * size
    stmt = stmt.offset(offset_value).limit(size)

    result = await db.execute(stmt)
    patients = result.scalars().all()
        
    return patients