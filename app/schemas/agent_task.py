from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.agent_task import TaskStatus


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    agent_mate_id: UUID
    agent_name: str | None
    status: TaskStatus
    depth: int
    parent_task_id: UUID | None
    trigger_message_id: UUID
    error: str | None
    created_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None