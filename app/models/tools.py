import uuid
from app.db.database import Base
from sqlalchemy import UniqueConstraint, Column, Uuid, String, DateTime, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Tools(Base):
    __tablename__ = "tools"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, unique=True, nullable=False)
    name = Column(String)
    desc = Column(String)
    created_by = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)  # audit only

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True))

    public_safe = Column(Boolean, nullable=False, default=False)
    requires_approval = Column(Boolean, nullable=False, default=False)

    agent_tool = relationship("AgentTools", back_populates="tool")


class AgentTools(Base):
    __tablename__ = "agent_tools"
    __table_args__ = (UniqueConstraint("agent_mate_id", "tool_id"),)

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_mate_id = Column(Uuid(as_uuid=True), ForeignKey("agent_mates.id"), nullable=False)
    tool_id = Column(Uuid(as_uuid=True), ForeignKey("tools.id"), nullable=False)
    attached_by = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)  # audit only

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True))

    tool = relationship("Tools", back_populates="agent_tool")
    agent = relationship("MateAgent", back_populates="agent_tool")
