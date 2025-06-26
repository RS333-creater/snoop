from sqlalchemy.orm import Session
from models import User, Habit
from schemas import UserCreate, UserUpdate, HabitUpdate, NotificationUpdate,NotificationCreate
from datetime import datetime ,timezone, date, time as time_type
from passlib.context import CryptContext
import hashlib
import security 
import models
import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_user(db: Session, user_data: UserCreate):
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=security.pwd_context.hash(user_data.password), 
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

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
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

def get_habit(db: Session, habit_id: int):
    return db.query(Habit).filter(Habit.id == habit_id).first()

def get_habits(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Habit).offset(skip).limit(limit).all()

def get_habits_by_user(db: Session, user_id: int):
    """ユーザーIDに基づいて、そのユーザーのすべての習慣を取得する"""
    return db.query(models.Habit).filter(models.Habit.user_id == user_id).all()


def update_habit(db: Session, habit_id: int, habit_data: HabitUpdate):
    db_habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not db_habit:
        return None
    for field, value in habit_data.dict(exclude_unset=True).items():
        setattr(db_habit, field, value)
    db.commit()
    db.refresh(db_habit)
    return db_habit

def create_habit(db: Session, habit_data: schemas.HabitCreate, user_id: int):
    """新しい習慣を作成する"""
    db_habit = models.Habit(
        user_id=user_id,
        name=habit_data.name,
        description=habit_data.description,
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
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

def get_habit_records_by_date_range(db: Session, habit_id: int, start_date: date, end_date: date):
    """
    指定された習慣IDと期間に基づいて、習慣の記録を取得する
    """
    return db.query(models.HabitRecord).filter(
        models.HabitRecord.habit_id == habit_id,
        models.HabitRecord.date.between(start_date, end_date)
    ).order_by(models.HabitRecord.date).all()

def create_notification(db: Session, notification: schemas.NotificationCreate, user_id: int):
    """新しい通知を作成する"""
    db_notification = models.Notification(
        user_id=user_id,
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
    update_data = notification_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_notification, key, value)
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

def create_goal_for_habit(db: Session, goal: schemas.GoalCreate, habit_id: int):
    """特定の習慣に新しい目標を作成する"""
    db_goal = models.Goal(
        **goal.dict(),  
        habit_id=habit_id
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def get_goal(db: Session, goal_id: int):
    """IDで単一の目標を取得する"""
    return db.query(models.Goal).filter(models.Goal.id == goal_id).first()

def get_goals_for_habit(db: Session, habit_id: int):
    """特定の習慣に紐づくすべての目標を取得する"""
    return db.query(models.Goal).filter(models.Goal.habit_id == habit_id).all()

def update_goal(db: Session, goal_id: int, goal_update: schemas.GoalCreate):
    """目標を更新する"""
    db_goal = get_goal(db, goal_id)
    if db_goal:
        update_data = goal_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_goal, key, value)
        db.commit()
        db.refresh(db_goal)
    return db_goal

def delete_goal(db: Session, goal_id: int):
    """目標を削除する"""
    db_goal = get_goal(db, goal_id)
    if db_goal:
        db.delete(db_goal)
        db.commit()
    return db_goal

def get_notifications_by_time(db: Session, time_str: str):
    """指定された時刻（HH:MM）に設定されている有効な通知をすべて取得する"""
    hour, minute = map(int, time_str.split(':'))
    target_time = time_type(hour, minute)
    
    return db.query(models.Notification).filter(
        models.Notification.time == target_time,
        models.Notification.enabled == True
    ).all()
    
def update_user_fcm_token(db: Session, user_id: int, fcm_token: str):
    """ユーザーのFCMトークンを更新または設定する"""
    db_user = get_user(db, user_id=user_id)
    if db_user:
        db_user.fcm_token = fcm_token
        db.commit()
        db.refresh(db_user)
    return db_user

def get_notifications_for_habit(db: Session, habit_id: int):
    """特定の習慣IDに紐づくすべての通知を取得する"""
    return db.query(models.Notification).filter(models.Notification.habit_id == habit_id).all()