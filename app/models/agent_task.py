import uuid
from datetime import datetime, timezone
from enum import Enum as EnumClass
from app.db.database import Base
from sqlalchemy import Column, Uuid, String, Integer, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship


class TaskStatus(str, EnumClass):
    queued = "queued"
    running = "running"
    awaiting_approval = "awaiting_approval"
    done = "done"
    cancelled = "cancelled"
    failed = "failed"


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(Uuid(as_uuid=True), ForeignKey("conversations.session_id"), nullable=False)
    agent_mate_id = Column(Uuid(as_uuid=True), ForeignKey("agent_mates.id"), nullable=False)
    trigger_message_id = Column(Uuid(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    acting_user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    requested_by_agent_id = Column(Uuid(as_uuid=True), ForeignKey("agent_mates.id"), nullable=True)
    parent_task_id = Column(Uuid(as_uuid=True), ForeignKey("agent_tasks.id"), nullable=True)
    file_id = Column(Uuid(as_uuid=True), ForeignKey("files.id"), nullable=True)

    depth = Column(Integer, nullable=False, default=0)
    instruction = Column(String)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.queued)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))

    agent = relationship("MateAgent", foreign_keys=[agent_mate_id])

    @property
    def agent_name(self) -> str | None:
        return self.agent.agent_name if self.agent else None