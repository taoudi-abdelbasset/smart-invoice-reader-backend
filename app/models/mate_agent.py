import uuid
from app.db.database import Base
from sqlalchemy import UniqueConstraint, Column, Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class MateAgent(Base):
    __tablename__ = "agent_mates"
    __table_args__ = (UniqueConstraint("user_id", "agent_id"),)

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String)
    agent_id = Column(String, nullable=False)
    desc = Column(String)
    role = Column(String)
    system_prompt = Column(String)

    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="agents")
    agent_tool = relationship("AgentTools", back_populates="agent")

    @property
    def tools(self):
        return [
            at.tool for at in self.agent_tool
            if not at.deleted_at and not at.tool.deleted_at
        ]