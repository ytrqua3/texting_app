from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    id: int

class ChatroomResponse(BaseModel):
    name: str
    id: int

class ChatroomParticipantResponse(BaseModel):
    user_id: int
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)

class ChatroomCreate(BaseModel):
    name: str

class MessageResponse(BaseModel):
    owner_id: int
    created_at: datetime
    content: str