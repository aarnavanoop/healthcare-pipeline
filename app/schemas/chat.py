from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    patient_id: str