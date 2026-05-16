import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from arq.connections import RedisSettings
from app.rag.pipeline import generate_embedding, client
from app.db.session import AsyncSessionLocal
from app.db.models import PatientNote, Patient
from sqlalchemy import select

async def generate_and_embed_note(ctx, patient_id: str):
    async with AsyncSessionLocal() as session:
        # 1. Fetch the patient data
        result = await session.execute(select(Patient).where(Patient.patient_id == patient_id))
        patient = result.scalar_one_or_none()
        
        if not patient:
            return False

        # 2. Generate the clinical note via OpenAI
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
        note_text = response.choices[0].message.content

        # 3. Create the vector embedding
        embedding = await generate_embedding(note_text)
        
        # 4. Save to pgvector
        new_note = PatientNote(
            patient_id=patient.patient_id,
            note_text=note_text,
            embedding=embedding
        )
        session.add(new_note)
        await session.commit()
        
    return True

class WorkerSettings:
    functions = [generate_and_embed_note]
    redis_settings = RedisSettings(host='redis', port=6379)