from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class ToolsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    key: str
    name: str
    desc: str
    created_at: datetime
    deleted_at: datetime | None

class NewAgentTool(BaseModel):
    tool_id: UUID

class ToolsCreate(BaseModel):
    key: str
    name: str
    desc: str

class ToolsUpdate(BaseModel):
    name: str | None = None
    desc: str | None = None