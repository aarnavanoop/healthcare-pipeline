import asyncio
import os
import sys
from sqlalchemy.future import select
from openai import AsyncOpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal
from app.db.models import Patient, PatientNote
from app.rag.pipeline import generate_embedding

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_clinical_note(patient: Patient) -> str:
    prompt = f"""
    Age: {patient.age}
    Resting Blood Pressure: {patient.resting_blood_pressure}
    Cholesterol: {patient.serum_cholestrol}
    Max Heart Rate: {patient.max_heart_rate}
    Anomaly Flagged: {patient.is_anomaly}
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a medical professional writing concise clinical notes based on patient telemetry."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Patient).where(Patient.is_anomaly == True))
        anomalous_patients = result.scalars().all()

        for patient in anomalous_patients:
            note_text = await generate_clinical_note(patient)
            embedding = await generate_embedding(note_text)
            
            new_note = PatientNote(
                patient_id=patient.patient_id,
                note_text=note_text,
                embedding=embedding
            )
            session.add(new_note)
        
        await session.commit()

if __name__ == "__main__":
    asyncio.run(main())