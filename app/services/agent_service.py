from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from app.models.mate_agent import MateAgent
from app.models.tools import Tools, AgentTools
from app.schemas.agent import MateAgentCreate, MateAgentUpdate

def _agent_query(db: Session):
    return db.query(MateAgent).options(
        joinedload(MateAgent.agent_tool).joinedload(AgentTools.tool)
    )

def list_agents(db: Session):
    """All agents, shared with every user."""
    return (
        _agent_query(db)
        .filter(MateAgent.deleted_at.is_(None))
        .order_by(MateAgent.created_at.desc())
        .all()
    )

def list_user_agents(db: Session, user_id: UUID):
    """Only the agents created by this user."""
    return (
        _agent_query(db)
        .filter(MateAgent.user_id == user_id, MateAgent.deleted_at.is_(None))
        .order_by(MateAgent.created_at.desc())
        .all()
    )

def get_agent_by_id(db: Session, agent_mate_id: UUID) -> MateAgent | None:
    """Anyone can read / use an agent."""
    return (
        _agent_query(db)
        .filter(MateAgent.id == agent_mate_id, MateAgent.deleted_at.is_(None))
        .first()
    )

def get_agent_by_slug(db: Session, agent_id: str) -> MateAgent | None:
    """Used to resolve @agent_id tags."""
    return (
        _agent_query(db)
        .filter(MateAgent.agent_id == agent_id, MateAgent.deleted_at.is_(None))
        .first()
    )

def get_owned_agent(db: Session, agent_mate_id: UUID, user_id: UUID) -> MateAgent:
    """Fetch an agent for modification: it must exist and belong to the user."""
    agent = get_agent_by_id(db, agent_mate_id)
    if not agent:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Agent not found.")
    if agent.user_id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can modify this agent.")
    return agent

def create_agent(db: Session, user_id: UUID, data: MateAgentCreate) -> MateAgent:
    exists = db.query(MateAgent).filter(MateAgent.agent_id == data.agent_id).first()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Agent id '{data.agent_id}' is already used.")

    agent = MateAgent(**data.model_dump(), user_id=user_id)
    db.add(agent)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Agent id already used.")
    db.refresh(agent)
    return agent

def update_agent(db: Session, agent: MateAgent, data: MateAgentUpdate) -> MateAgent:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    db.commit()
    db.refresh(agent)
    return agent

def delete_agent(db: Session, agent: MateAgent) -> None:
    agent.deleted_at = func.now()
    db.commit()

def attach_tool(db: Session, agent: MateAgent, tool_id: UUID, user_id: UUID) -> MateAgent:
    tool = db.query(Tools).filter(Tools.id == tool_id, Tools.deleted_at.is_(None)).first()
    if not tool:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tool not found.")

    link = (
        db.query(AgentTools)
        .filter(AgentTools.agent_mate_id == agent.id, AgentTools.tool_id == tool_id)
        .first()
    )
    if link and link.deleted_at is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Tool already attached to this agent.")

    if link:  
        link.deleted_at = None
        link.attached_by = user_id
    else:
        db.add(AgentTools(agent_mate_id=agent.id, tool_id=tool_id, attached_by=user_id))

    db.commit()
    db.refresh(agent)
    return agent

def detach_tool(db: Session, agent: MateAgent, tool_id: UUID) -> MateAgent:
    link = (
        db.query(AgentTools)
        .filter(
            AgentTools.agent_mate_id == agent.id,
            AgentTools.tool_id == tool_id,
            AgentTools.deleted_at.is_(None),
        )
        .first()
    )
    if not link:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tool is not attached to this agent.")

    link.deleted_at = func.now()
    db.commit()
    db.refresh(agent)
    return agent

def sync_tools(db: Session, registry: dict[str, dict]) -> None:
    """registry = {"invoice_tools": {"name": "...", "desc": "..."}, ...}
    Call on app startup. Safe to run on every boot."""
    existing = {t.key: t for t in db.query(Tools).all()}

    for key, meta in registry.items():
        tool = existing.get(key)
        if tool is None:
            db.add(Tools(key=key, name=meta["name"], desc=meta["desc"]))
        else:
            tool.name, tool.desc, tool.deleted_at = meta["name"], meta["desc"], None

    for key, tool in existing.items():  
        if key not in registry and tool.deleted_at is None:
            tool.deleted_at = func.now()

    db.commit()