from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    created_at: datetime