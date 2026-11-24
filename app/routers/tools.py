from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.auth_serivce import get_current_user
from app.models.user import User
from app.schemas.agent_tools import ToolsCreate, ToolsUpdate, ToolsOut
from app.services import tools_service

router = APIRouter(prefix="/tools", tags=["tools"])

@router.get("/", response_model=list[ToolsOut])
def list_tools(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return tools_service.list_tools(db)

@router.get("/{tool_id}", response_model=ToolsOut)
def get_tool(tool_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return tools_service.get_tool(db, tool_id)
