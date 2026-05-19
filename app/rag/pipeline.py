import uuid
import os
from openai import AsyncOpenAI
from typing import List, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import PatientNote

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_embedding(text_input: str) -> List[float]:
    """Step 1: Embed the incoming query."""
    response = await client.embeddings.create(
        input=text_input,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

async def retrieve_context(session: AsyncSession, query_embedding: List[float], patient_id: str, top_k: int = 3) -> List[str]:
    """Step 2: Cosine similarity search in pgvector strictly filtered by patient ID."""
    patient_uuid = uuid.UUID(patient_id)   
    stmt = select(PatientNote).where(
        PatientNote.patient_id == patient_uuid
    ).order_by(
        PatientNote.embedding.cosine_distance(query_embedding)
    ).limit(top_k)
    
    result = await session.execute(stmt)
    notes = result.scalars().all()
    return [note.note_text for note in notes]

def build_prompt(query: str, context_notes: List[str]) -> str:
    """Step 3: Inject retrieved context into the system prompt."""
    context_str = "\n\n".join([f"Clinical Note {i+1}:\n{note}" for i, note in enumerate(context_notes)])
    
    return f"""
    You are an AI medical assistant triaging patient data. 
    Answer the user's question using ONLY the provided clinical notes as context.
    If the answer is not contained in the notes, say "I do not have enough information in the patient record to answer that."
    
    Context Notes:
    {context_str}
    
    User Question: {query}
    """

async def generate_chat_response(session: AsyncSession, query: str, patient_id: str) -> str:
    """Step 4: Standard OpenAI completion using the augmented prompt filtered by patient ID."""
    query_embedding = await generate_embedding(query)
    context_notes = await retrieve_context(session, query_embedding, patient_id)
    prompt = build_prompt(query, context_notes)
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise, professional medical AI assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

async def generate_chat_stream(session: AsyncSession, query: str, patient_id: str) -> AsyncGenerator[str, None]:
    """Step 4 (Alternative): Streaming OpenAI completion for the frontend UI filtered by patient ID."""
    query_embedding = await generate_embedding(query)
    context_notes = await retrieve_context(session, query_embedding, patient_id)
    prompt = build_prompt(query, context_notes)
    
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise, professional medical AI assistant."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content