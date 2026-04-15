from pydantic import BaseModel, ConfigDict
from datetime import date

class PatientVitals(BaseModel):

    resting_blood_pressure: float
    serum_cholestrol: float
    fasting_blood_sugar: float
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
    

class PatientResponse(BaseModel):
    patient_id: UUID
    age: int
    sex: int

    vitals: PatientVitals

    diagnosis_of_disease: int
    is_anomaly: bool

    model_config = ConfigDict(from_attributes=True)


class PatientSummary(BaseModel):
    patient_id: UUID
    age: int
    sex: int
    diagnosis_of_disease: int
    is_anomaly: bool

    model_config = ConfigDict(from_attributes=True)

