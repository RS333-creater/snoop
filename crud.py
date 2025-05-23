from sqlalchemy.orm import Session
from models import User, Habit
from schemas import UserCreate, UserUpdate, HabitUpdate
from datetime import datetime ,timezone
import models
import schemas
from passlib.context import CryptContext

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_user(db: Session, user_data: UserCreate):
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),  
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, user_id: int, user_data: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

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

def get_habit(db: Session, habit_id: int):
    return db.query(Habit).filter(Habit.id == habit_id).first()

def get_habits(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Habit).offset(skip).limit(limit).all()

def update_habit(db: Session, habit_id: int, habit_data: HabitUpdate):
    db_habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not db_habit:
        return None
    for field, value in habit_data.dict(exclude_unset=True).items():
        setattr(db_habit, field, value)
    db.commit()
    db.refresh(db_habit)
    return db_habit

def delete_habit(db: Session, habit_id: int):
    db_habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not db_habit:
        return None
    db.delete(db_habit)
    db.commit()
    return db_habit