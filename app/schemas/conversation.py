from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from app.schemas.user import UserOut
from app.schemas.message import MessageBody

class UploadedMiniFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    file_name: str
    is_proccesed: bool
    conversation_id: UUID
    created_at: datetime

class ConversationOut(BaseModel):
    user_id : UUID
    session_id: UUID
    
    title:str
    
    created_at: datetime
    user: UserOut
    files: list[UploadedMiniFile]
    messages: list[MessageBody]

class ConversationCreate(BaseModel):
    title: str

class ConversationUpdate(BaseModel):
    title: str | None = None