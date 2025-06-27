# schemas.py (最終・修正版)

from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date, time
from typing import Optional

# --- ★★★ HabitCreateから user_id を削除しました ★★★ ---
# これが今回の修正の核心です。
# user_idはリクエストボディで送るのではなく、
# ログインしているユーザーのトークンから自動で取得するためです。
class HabitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="ランニング")
    description: Optional[str] = Field(None, example="毎朝30分走る")

class HabitResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True
        
class UserCreate(BaseModel):
    name: str = Field(..., example="山田太郎")
    email: EmailStr = Field(..., example="taro@example.com")
    password: str 

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True
        
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True

class UserVerify(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
        
class HabitRecordCreate(BaseModel):
    habit_id: int
    date: date
    status: bool

class HabitRecordResponse(BaseModel):
    id: int
    habit_id: int
    date: date
    status: bool

    class Config:
        from_attributes = True

class HabitRecordUpdate(BaseModel):
    date: Optional[date] = None
    status: Optional[bool] = None

    class Config:
        from_attributes = True
        
class NotificationCreate(BaseModel):
    habit_id: int
    time: time
    enabled: Optional[bool] = True

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    habit_id: int
    time: time
    enabled: bool

    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    time: Optional[time] = None
    enabled: Optional[bool] = None

    class Config:
        from_attributes = True
        
class GoalBase(BaseModel):
    target_count: int = Field(..., gt=0, example=10)
    start_date: date
    end_date: date

class GoalCreate(GoalBase):
    pass

class GoalResponse(GoalBase):
    id: int
    habit_id: int
    created_at: datetime
    current_count: int
    is_achieved: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class MessageResponse(BaseModel):
    message: str

class FCMTokenUpdate(BaseModel):
    fcm_token: str
