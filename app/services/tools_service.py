from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.tools import Tools
from app.schemas.agent_tools import ToolsCreate, ToolsUpdate
from app.agents.tool_registry import TOOL_REGISTRY


def list_tools(db: Session):
    return db.query(Tools).filter(Tools.deleted_at.is_(None)).order_by(Tools.name).all()

def get_tool(db: Session, tool_id: UUID) -> Tools:
    tool = db.query(Tools).filter(Tools.id == tool_id, Tools.deleted_at.is_(None)).first()
    if not tool:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tool not found.")
    return tool

def create_tool(db: Session, user_id: UUID, data: ToolsCreate) -> Tools:
    if data.key not in TOOL_REGISTRY:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Unknown tool key '{data.key}'. Valid keys: {', '.join(TOOL_REGISTRY)}",
        )

    existing = db.query(Tools).filter(Tools.key == data.key).first()
    if existing and existing.deleted_at is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Tool key already exists.")

    if existing:
        existing.name, existing.desc = data.name, data.desc
        existing.deleted_at = None
        tool = existing
    else:
        tool = Tools(**data.model_dump(), created_by=user_id)
        db.add(tool)

    db.commit()
    db.refresh(tool)
    return tool

def update_tool(db: Session, tool: Tools, data: ToolsUpdate) -> Tools:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tool, field, value)
    db.commit()
    db.refresh(tool)
    return tool

def delete_tool(db: Session, tool: Tools) -> None:
    tool.deleted_at = func.now()
    db.commit()

def sync_registry_to_db(db: Session) -> None:
    existing = {t.key: t for t in db.query(Tools).all()}
    for key, meta in TOOL_REGISTRY.items():
        tool = existing.get(key)
        if tool is None:
            db.add(Tools(key=key, name=meta["name"], desc=meta["desc"],
                         public_safe=meta["public_safe"],
                         requires_approval=meta["requires_approval"]))
        else:
            tool.public_safe = meta["public_safe"]
            tool.requires_approval = meta["requires_approval"]
    db.commit()