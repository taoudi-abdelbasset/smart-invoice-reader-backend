from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from app.schemas.agent_tools import ToolsOut


class MateAgentCreate(BaseModel):
    agent_name: str
    agent_id: str = Field(pattern=r"^[a-z0-9_]+$")
    desc: str
    role: str
    system_prompt: str

class MateAgentUpdate(BaseModel):
    agent_name: str | None = None
    desc: str | None = None
    role: str | None = None
    system_prompt: str | None = None

class MateAgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    agent_name: str
    agent_id: str
    desc: str
    role: str
    system_prompt: str
    tools: list[ToolsOut]
    created_at: datetime
    deleted_at: datetime | None