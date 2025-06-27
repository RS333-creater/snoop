from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone, date, time as time_type

# security.pyの関数を正しく使うためにインポート
import models, schemas, security

# --- User CRUD ---
def get_user(db: Session, user_id: int):
    """IDで単一のユーザーを取得する"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """メールアドレスで単一のユーザーを取得する"""
    return db.query(models.User).filter(models.User.email == email).first()

def create_or_update_unverified_user(db: Session, user_data: schemas.UserCreate) -> models.User:
    """
    ユーザーが存在しない場合は新規作成し、
    未認証で存在する場合には認証コードとパスワードを更新する。
    """
    db_user = get_user_by_email(db, user_data.email)
    
    verification_code = security.create_verification_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    if db_user and not db_user.is_verified:
        # ユーザーが「未認証」で存在する場合、コードとパスワードを更新
        db_user.password_hash = security.get_password_hash(user_data.password)
        db_user.verification_code = verification_code
        db_user.verification_code_expires_at = expires_at
        db_user.name = user_data.name
        user_to_return = db_user
    else:
        # ユーザーが存在しない場合、新規作成
        hashed_password = security.get_password_hash(user_data.password)
        new_user = models.User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            created_at=datetime.now(timezone.utc),
            is_verified=False,
            verification_code=verification_code,
            verification_code_expires_at=expires_at
        )
        db.add(new_user)
        user_to_return = new_user

    db.commit()
    db.refresh(user_to_return)
    return user_to_return

def verify_user_code(db: Session, email: str, code: str) -> models.User | None:
    """ユーザーの認証コードを検証する"""
    user = get_user_by_email(db, email)
    if not user or user.is_verified:
        return None
    
    if user.verification_code == code and user.verification_code_expires_at > datetime.now(timezone.utc):
        user.is_verified = True
        user.verification_code = None
        user.verification_code_expires_at = None
        db.commit()
        db.refresh(user)
        return user
    return None

def update_user_fcm_token(db: Session, user_id: int, fcm_token: str):
    """ユーザーのFCMトークンを更新または設定する"""
    db_user = get_user(db, user_id=user_id)
    if db_user:
        db_user.fcm_token = fcm_token
        db.commit()
        db.refresh(db_user)
    return db_user

# --- Habit CRUD ---
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
    
def get_habits_by_user(db: Session, user_id: int):
    """ユーザーIDに基づいて、そのユーザーのすべての習慣を取得する"""
    return db.query(models.Habit).filter(models.Habit.user_id == user_id).all()

def get_habit(db: Session, habit_id: int):
    return db.query(models.Habit).filter(models.Habit.id == habit_id).first()

def update_habit(db: Session, habit_id: int, habit_data: schemas.HabitUpdate):
    """習慣を更新する"""
    db_habit = get_habit(db, habit_id=habit_id)
    if db_habit:
        update_data = habit_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_habit, key, value)
        db.commit()
        db.refresh(db_habit)
    return db_habit

def delete_habit(db: Session, habit_id: int):
    """習慣を削除する"""
    db_habit = get_habit(db, habit_id=habit_id)
    if db_habit:
        db.delete(db_habit)
        db.commit()
    return db_habit

# --- HabitRecord CRUD ---
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

def get_habit_records_by_date_range(db: Session, habit_id: int, start_date: date, end_date: date):
    return db.query(models.HabitRecord).filter(
        models.HabitRecord.habit_id == habit_id,
        models.HabitRecord.date.between(start_date, end_date)
    ).order_by(models.HabitRecord.date).all()
    
# --- Goal CRUD ---
def create_goal_for_habit(db: Session, goal: schemas.GoalCreate, habit_id: int):
    db_goal = models.Goal(
        habit_id=habit_id,
        target_count=goal.target_count,
        start_date=goal.start_date,
        end_date=goal.end_date
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

# --- Notification CRUD ---
def create_notification(db: Session, notification: schemas.NotificationCreate, user_id: int):
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

def get_notifications_for_habit(db: Session, habit_id: int):
    return db.query(models.Notification).filter(models.Notification.habit_id == habit_id).all()

def get_notification(db: Session, notification_id: int):
    return db.query(models.Notification).filter(models.Notification.id == notification_id).first()

def update_notification(db: Session, notification_id: int, notification_update: schemas.NotificationUpdate):
    db_notification = get_notification(db, notification_id)
    if db_notification:
        update_data = notification_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_notification, key, value)
        db.commit()
        db.refresh(db_notification)
    return db_notification

def delete_notification(db: Session, notification_id: int):
    db_notification = get_notification(db, notification_id)
    if db_notification:
        db.delete(db_notification)
        db.commit()
    return db_notification

def get_notifications_by_time(db: Session, time_str: str):
    hour, minute = map(int, time_str.split(':'))
    target_time = time_type(hour, minute)
    
    return db.query(models.Notification).filter(
        models.Notification.time == target_time,
        models.Notification.enabled == True
    ).all()
