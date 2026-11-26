from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.message import MessageRole

class SendMessage(BaseModel):
    content: str = Field(min_length=1)

class MessageBody(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    conversation_id: UUID
    content: str | None
    role: MessageRole
    sender_user_id: UUID | None
    sender_agent_mate_id: UUID | None
    sender_name: str | None
    mentions: list | None
    file_id: UUID | None
    created_at: datetime | None