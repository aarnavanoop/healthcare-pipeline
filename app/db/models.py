from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Float, Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.session import Base

class Patient(Base):
    __tablename__ = 'patients'

    __table_args__ = {"schema": "healthcare_data"}

    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    age: Mapped[float]
    sex: Mapped[int]
    resting_blood_pressure: Mapped[float]
    serum_cholestrol: Mapped[float]
    fasting_blood_sugar: Mapped[int]
    max_heart_rate: Mapped[float]
    exercise_induced_angina: Mapped[int]
    st_depression_induced: Mapped[float]
    number_of_vessels: Mapped[float]
    diagnosis_of_disease: Mapped[int]

    chest_pain_2: Mapped[int] = mapped_column("chest_pain_2.0")
    chest_pain_3: Mapped[int] = mapped_column("chest_pain_3.0")
    chest_pain_4: Mapped[int] = mapped_column("chest_pain_4.0")
    
    resting_ecg_1: Mapped[int] = mapped_column("resting_ecg_1.0")
    resting_ecg_2: Mapped[int] = mapped_column("resting_ecg_2.0")
    
    thal_6: Mapped[int] = mapped_column("thal_6.0")
    thal_7: Mapped[int] = mapped_column("thal_7.0")
    
    slope_peak_2: Mapped[int] = mapped_column("slope_peak_2.0")
    slope_peak_3: Mapped[int] = mapped_column("slope_peak_3.0")
    
    is_anomaly: Mapped[bool]

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


