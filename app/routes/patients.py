from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import logging
import uuid
from app.db.deps import get_db
from app.db.models import Patient

logger = logging.getLogger("api_engine.patients")

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

# --- Pydantic Schemas ---

class VitalsSchema(BaseModel):
    resting_blood_pressure: float
    serum_cholestrol: float
    fasting_blood_sugar: int
    max_heart_rate: float
    exercise_induced_angina: int
    st_depression_induced: float
    number_of_vessels: float
    chest_pain_2: int
    chest_pain_3: int
    chest_pain_4: int
    resting_ecg_1: int
    resting_ecg_2: int
    thal_6: int
    thal_7: int
    slope_peak_2: int
    slope_peak_3: int

class PatientDetailResponse(BaseModel):
    patient_id: uuid.UUID
    age: float
    sex: int
    diagnosis_of_disease: int
    is_anomaly: bool
    vitals: VitalsSchema

# --- Endpoints ---

@router.get("/")
async def get_patients(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    anomaly_flag: Optional[bool] = Query(None, description="Filter by anomaly presence"),
):
    """
    Returns a paginated list of patients
    """
    logger.info(f"Fetching patient list -> page: {page}, size: {size}")

    stmt = select(Patient)
    if anomaly_flag is not None:
        stmt = stmt.where(Patient.is_anomaly == anomaly_flag)

    offset_value = (page - 1) * size
    stmt = stmt.offset(offset_value).limit(size)

    result = await db.execute(stmt)
    patients = result.scalars().all()
        
    return patients


@router.get("/{patient_id}", response_model=PatientDetailResponse)
async def get_patient_id(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns a single patient by their UUID, including fully nested vitals.
    """
    logger.info(f"Fetching patient id: {patient_id}")

    stmt = select(Patient).where(Patient.patient_id == patient_id)
    result = await db.execute(stmt)
    db_patient = result.scalar_one_or_none()

    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    vitals_data = VitalsSchema(
        resting_blood_pressure=db_patient.resting_blood_pressure,
        serum_cholestrol=db_patient.serum_cholestrol,
        fasting_blood_sugar=db_patient.fasting_blood_sugar,
        max_heart_rate=db_patient.max_heart_rate,
        exercise_induced_angina=db_patient.exercise_induced_angina,
        st_depression_induced=db_patient.st_depression_induced,
        number_of_vessels=db_patient.number_of_vessels,
        chest_pain_2=db_patient.chest_pain_2,
        chest_pain_3=db_patient.chest_pain_3,
        chest_pain_4=db_patient.chest_pain_4,
        resting_ecg_1=db_patient.resting_ecg_1,
        resting_ecg_2=db_patient.resting_ecg_2,
        thal_6=db_patient.thal_6,
        thal_7=db_patient.thal_7,
        slope_peak_2=db_patient.slope_peak_2,
        slope_peak_3=db_patient.slope_peak_3
    )
    

    return PatientDetailResponse(
        patient_id=db_patient.patient_id,
        age=db_patient.age,
        sex=db_patient.sex,
        diagnosis_of_disease=db_patient.diagnosis_of_disease,
        is_anomaly=db_patient.is_anomaly,
        vitals=vitals_data
    )