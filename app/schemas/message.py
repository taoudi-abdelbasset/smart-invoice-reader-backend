from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from app.models.message import MessageRole

class MessageBody(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    conversation_id: UUID
    content: str

    role: MessageRole
    
    created_at: datetime

class SendMessage(BaseModel):
    content: str
