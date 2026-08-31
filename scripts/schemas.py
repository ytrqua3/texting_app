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