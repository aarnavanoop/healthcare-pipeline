import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from arq.connections import RedisSettings
from app.rag.pipeline import generate_embedding
from app.db.session import AsyncSessionLocal
from app.db.models import PatientNote

async def embed_patient_note(ctx, patient_id: str, note_text: str):
    embedding = await generate_embedding(note_text)
    
    async with AsyncSessionLocal() as session:
        new_note = PatientNote(
            patient_id=patient_id,
            note_text=note_text,
            embedding=embedding
        )
        session.add(new_note)
        await session.commit()
        
    return True

class WorkerSettings:
    functions = [embed_patient_note]
    redis_settings = RedisSettings(host='redis', port=6379)