from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
class HabitCreate(BaseModel):
    user_id: int
    name: str = Field(..., min_length=1, max_length=100, example="ランニング")
    description: Optional[str] = Field(None, example="毎朝30分走る")
class HabitResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
class UserCreate(BaseModel):
    name: str = Field(..., example="山田太郎")
    email: EmailStr = Field(..., example="taro@example.com")
    password_hash: str  # もし平文パスワードならハッシュ化処理を別で

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True