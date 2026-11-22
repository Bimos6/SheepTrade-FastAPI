from pydantic import BaseModel, Field
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

class UserResponse(BaseModel):
    id: int
    username: str
    balance: int
    created_at: datetime

    class Config:
        from_attributes = True