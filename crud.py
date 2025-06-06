from sqlalchemy.orm import Session
from models import User, Habit
from schemas import UserCreate, UserUpdate, HabitUpdate, NotificationUpdate,NotificationCreate
from datetime import datetime ,timezone
import models
import schemas
from passlib.context import CryptContext
import hashlib

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


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


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

def create_habit_record(db: Session, record: schemas.HabitRecordCreate):
    db_record = models.HabitRecord(
        habit_id=record.habit_id,
        date=record.date,
        status=record.status
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_habit_record(db: Session, record_id: int):
    return db.query(models.HabitRecord).filter(models.HabitRecord.id == record_id).first()

def get_habit_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.HabitRecord).offset(skip).limit(limit).all()

def update_habit_record(db: Session, record_id: int, record_data: schemas.HabitRecordUpdate):
    db_record = db.query(models.HabitRecord).filter(models.HabitRecord.id == record_id).first()
    if not db_record:
        return None
    for field, value in record_data.dict(exclude_unset=True).items():
        setattr(db_record, field, value)
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_habit_record(db: Session, record_id: int):
    db_record = db.query(models.HabitRecord).filter(models.HabitRecord.id == record_id).first()
    if not db_record:
        return None
    db.delete(db_record)
    db.commit()
    return db_record

def create_notification(db: Session, notification: NotificationCreate):
    db_notification = models.Notification(
        user_id=notification.user_id,
        habit_id=notification.habit_id,
        time=notification.time,
        enabled=notification.enabled
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notification(db: Session, notification_id: int):
    return db.query(models.Notification).filter(models.Notification.id == notification_id).first()

def get_notifications(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Notification).offset(skip).limit(limit).all()

def update_notification(db: Session, notification_id: int, notification_update: NotificationUpdate):
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return None
    if notification_update.time is not None:
        db_notification.time = notification_update.time
    if notification_update.enabled is not None:
        db_notification.enabled = notification_update.enabled
    db.commit()
    db.refresh(db_notification)
    return db_notification

def delete_notification(db: Session, notification_id: int):
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return None
    db.delete(db_notification)
    db.commit()
    return db_notification
