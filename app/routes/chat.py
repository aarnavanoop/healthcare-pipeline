import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.db.deps import get_db
from app.db.models import RagAudit
from app.schemas.chat import ChatRequest
from app.rag.pipeline import generate_embedding, retrieve_context, build_prompt, client

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("")
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    async def event_generator():
        start_time = time.time()
        
        query_embedding = await generate_embedding(request.query)
        context_notes = await retrieve_context(db, query_embedding)
        prompt = build_prompt(request.query, context_notes)
        
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise, professional medical AI assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        
        full_response = ""
        
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield {"data": content}
        
        latency = (time.time() - start_time) * 1000
        
        audit = RagAudit(
            query=request.query,
            context_notes="\n---\n".join(context_notes),
            response_text=full_response,
            latency_ms=latency
        )
        db.add(audit)
        await db.commit()
        
        yield {"event": "done", "data": "[DONE]"}

    return EventSourceResponse(event_generator())