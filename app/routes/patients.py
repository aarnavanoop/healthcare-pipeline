from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict
import logging
import uuid
from app.db.deps import get_db
from app.db.models import Patient

logger = logging.getLogger("api_engine.patients")

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

# --- Helper Functions ---
def determine_severity(patient_record) -> str:
    """
    Derives severity from normalised (z-score) clinical columns.
    Values are StandardScaler output — magnitude indicates how far from average.
    abs(value) > 2 means 2+ standard deviations from mean, which is clinically significant.
    """
    if patient_record is None:
        return "LOW"
    
    severity_score = 0


    if patient_record.diagnosis_of_disease == 1:
        severity_score += 2


    if abs(patient_record.max_heart_rate) > 3:
        severity_score += 3
    elif abs(patient_record.max_heart_rate) > 2:
        severity_score += 2
    elif abs(patient_record.max_heart_rate) > 1:
        severity_score += 1

    if abs(patient_record.st_depression_induced) > 3:
        severity_score += 3
    elif abs(patient_record.st_depression_induced) > 2:
        severity_score += 2
    elif abs(patient_record.st_depression_induced) > 1:
        severity_score += 1

    if abs(patient_record.resting_blood_pressure) > 3:
        severity_score += 2
    elif abs(patient_record.resting_blood_pressure) > 2:
        severity_score += 1


    if patient_record.exercise_induced_angina == 1:
        severity_score += 1

    if severity_score >= 6:
        return "HIGH"
    elif severity_score >= 3:
        return "MEDIUM"
    else:
        return "LOW"


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

    model_config = ConfigDict(from_attributes=True)


class PatientDetailResponse(BaseModel):
    patient_id: uuid.UUID
    age: float
    sex: int
    diagnosis_of_disease: int
    is_anomaly: bool
    vitals: VitalsSchema

    model_config = ConfigDict(from_attributes=True)


class AnomalousDetailResponse(BaseModel):
    patient_id: uuid.UUID
    age: float
    sex: int
    diagnosis_of_disease: int
    is_anomaly: bool
    severity_level: str
    max_heart_rate: float
    st_depression_induced: float
    resting_blood_pressure: float
    exercise_induced_angina: int

    model_config = ConfigDict(from_attributes=True)


# --- Endpoints ---

@router.get("/anomalies", response_model=list[AnomalousDetailResponse])
async def get_anomalous_patients(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH"),
):
    """
    Returns a paginated list of anomalous patients with computed severity tiers.
    Severity is derived from normalised clinical columns — not stored in DB.
    Sorted HIGH -> MEDIUM -> LOW by default.
    """
    logger.info(f"Retrieving anomalous patients -> page: {page}, size: {size}, severity filter: {severity}")

    stmt = select(Patient).where(Patient.is_anomaly == True)
    offset_value = (page - 1) * size
    stmt = stmt.offset(offset_value).limit(size)

    result = await db.execute(stmt)
    patients = result.scalars().all()

    response = [
        AnomalousDetailResponse(
            patient_id=p.patient_id,
            age=p.age,
            sex=p.sex,
            diagnosis_of_disease=p.diagnosis_of_disease,
            is_anomaly=p.is_anomaly,
            severity_level=determine_severity(p),
            max_heart_rate=p.max_heart_rate,
            st_depression_induced=p.st_depression_induced,
            resting_blood_pressure=p.resting_blood_pressure,
            exercise_induced_angina=p.exercise_induced_angina,
        )
        for p in patients
    ]


    if severity:
        response = [r for r in response if r.severity_level == severity.upper()]


    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    response.sort(key=lambda r: severity_order[r.severity_level])

    return response


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