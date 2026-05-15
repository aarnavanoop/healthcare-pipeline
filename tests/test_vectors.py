import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.rag.pipeline import generate_embedding
from app.db.models import Patient, PatientNote
from app.db.session import AsyncSessionLocal

@pytest.mark.asyncio
async def test_generate_embedding_dimensions():
    text = "Patient presents with elevated heart rate."
    embedding = await generate_embedding(text)
    assert len(embedding) == 1536
    assert isinstance(embedding[0], float)

@pytest.mark.asyncio
async def test_vector_insertion():
    async with AsyncSessionLocal() as session:
        dummy_patient = Patient(
            patient_id=uuid.uuid4(),
            age=45.0,
            sex=1,
            resting_blood_pressure=120.0,
            serum_cholestrol=200.0,
            fasting_blood_sugar=0,
            max_heart_rate=150.0,
            exercise_induced_angina=0,
            st_depression_induced=1.0,
            number_of_vessels=0.0,
            diagnosis_of_disease=0,
            chest_pain_2=0,
            chest_pain_3=0,
            chest_pain_4=0,
            resting_ecg_1=0,
            resting_ecg_2=0,
            thal_6=0,
            thal_7=0,
            slope_peak_2=0,
            slope_peak_3=0,
            is_anomaly=False
        )
        session.add(dummy_patient)
        await session.commit()

        dummy_embedding = [0.1] * 1536
        
        note = PatientNote(
            patient_id=dummy_patient.patient_id,
            note_text="Dummy test note",
            embedding=dummy_embedding
        )
        session.add(note)
        await session.commit()

        assert note.id is not None