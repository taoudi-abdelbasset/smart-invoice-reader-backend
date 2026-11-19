from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.services import auth_serivce
from app.models.user import User
from app.schemas.agent import MateAgentCreate, MateAgentUpdate, MateAgentOut
from app.schemas.agent_tools import NewAgentTool
from app.services import agent_service

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/", response_model=list[MateAgentOut])
def list_agents(db: Session = Depends(get_db), user_id: UUID = Depends(auth_serivce.current_user_id)):
    return agent_service.list_agents(db)

# declared before "/{agent_mate_id}" so "mine" is not parsed as a UUID
@router.get("/mine", response_model=list[MateAgentOut])
def list_my_agents(db: Session = Depends(get_db), user_id: UUID = Depends(auth_serivce.current_user_id)):
    return agent_service.list_user_agents(db, user_id)


@router.get("/{agent_mate_id}", response_model=MateAgentOut)
def get_agent(agent_mate_id: UUID, db: Session = Depends(get_db), user_id: UUID = Depends(auth_serivce.current_user_id)):
    agent = agent_service.get_agent_by_id(db, agent_mate_id)
    if not agent:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Agent not found.")
    return agent

@router.post("/", response_model=MateAgentOut, status_code=status.HTTP_201_CREATED)
def create_agent(data: MateAgentCreate, db: Session = Depends(get_db), user_id: UUID = Depends(auth_serivce.current_user_id)):
    print("\n\n\n\t\t\t >>> ", user_id)
    return agent_service.create_agent(db, user_id, data)

@router.patch("/{agent_mate_id}", response_model=MateAgentOut)
def update_agent(
    agent_mate_id: UUID,
    data: MateAgentUpdate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(auth_serivce.current_user_id),
):
    agent = agent_service.get_owned_agent(db, agent_mate_id, user_id)
    return agent_service.update_agent(db, agent, data)

@router.delete("/{agent_mate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_mate_id: UUID, db: Session = Depends(get_db), user_id: UUID = Depends(auth_serivce.current_user_id)):
    agent = agent_service.get_owned_agent(db, agent_mate_id, user_id)
    agent_service.delete_agent(db, agent)

@router.post("/{agent_mate_id}/tools", response_model=MateAgentOut, status_code=status.HTTP_201_CREATED)
def attach_tool(
    agent_mate_id: UUID,
    data: NewAgentTool,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(auth_serivce.current_user_id),
):
    agent = agent_service.get_owned_agent(db, agent_mate_id, user_id)
    return agent_service.attach_tool(db, agent, data.tool_id, user_id)

@router.delete("/{agent_mate_id}/tools/{tool_id}", response_model=MateAgentOut)
def detach_tool(
    agent_mate_id: UUID,
    tool_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(auth_serivce.current_user_id),
):
    agent = agent_service.get_owned_agent(db, agent_mate_id, user_id)
    return agent_service.detach_tool(db, agent, tool_id)