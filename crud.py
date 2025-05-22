from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate
from datetime import datetime ,timezone
import models
import schemas

def create_user(db: Session, user_data: UserCreate):
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=user_data.password_hash,  # ハッシュ化済みを渡す想定
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_habit(db: Session, habit: schemas.HabitCreate, user_id: int):
    db_habit = models.Habit(
        user_id=habit.user_id,
        name=habit.name,
        description=habit.description,
        created_at=datetime.utcnow()
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit