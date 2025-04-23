from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
class HabitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="ランニング")
    description: Optional[str] = Field(None, example="毎朝30分走る")
class HabitResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime