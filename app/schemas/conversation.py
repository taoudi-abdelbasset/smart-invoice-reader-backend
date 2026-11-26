from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.conversation import ConversationVisibility
from app.models.conversation_member import MemberType, MemberRole

class ConversationCreate(BaseModel):
    title: str | None = None
    visibility: ConversationVisibility = ConversationVisibility.private
    default_agent_id: UUID | None = None

class ConversationUpdate(BaseModel):
    title: str | None = None

class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    session_id: UUID
    user_id: UUID
    title: str | None
    visibility: ConversationVisibility
    default_agent_id: UUID | None
    created_at: datetime | None

class PublicConversationOut(BaseModel):
    session_id: UUID
    title: str | None
    owner_username: str | None
    member_count: int
    is_member: bool
    created_at: datetime | None

class MemberOut(BaseModel):
    id: UUID
    member_type: MemberType
    role: MemberRole
    user_id: UUID | None
    agent_mate_id: UUID | None
    name: str | None
    handle: str | None
    joined_at: datetime | None

class AddAgentBody(BaseModel):
    agent_mate_id: UUID