from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date, time
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
    user_id: int
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
        
class Token(BaseModel):
    access_token: str
    token_type: str
    
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
    
    # API側で計算して追加するフィールド
    current_count: int
    is_achieved: bool

    class Config:
        from_attributes = True