from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from app.schemas.user import UserOut


class ConversationMiniBody(BaseModel):
    user_id : UUID
    session_id: UUID
    
    title:str
    
    created_at: datetime
    user : UserOut

class UploadedFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    file_name: str
    is_proccesed: bool
    conversation_id: UUID
    conversation: ConversationMiniBody
    created_at: datetime

class UploadedMiniFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    file_name: str
    conversation_id: UUID
    created_at: datetime