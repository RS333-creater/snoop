from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, date
from contextlib import asynccontextmanager

import firebase  
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from notification_sender import send_scheduled_notifications
from database import SessionLocal, engine
import models, crud, schemas, security

scheduler = AsyncIOScheduler(timezone="Asia/Tokyo")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションの起動時と終了時に処理を実行する"""
    print("Starting up...")
    scheduler.add_job(send_scheduled_notifications, 'interval', minutes=1, id="notification_job")
    scheduler.start()
    print("Scheduler started...")
    yield
    print("Shutting down...")
    scheduler.shutdown()
    print("Scheduler shut down...")

app = FastAPI(
    title="Snoop - Habit Tracker API",
    description="あなたの習慣を管理し、目標達成をサポートするAPIです。",
    version="1.0.0",
    lifespan=lifespan
)

def get_db():
    """データベースセッションを取得する依存性関数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.User:
    """トークンを検証し、現在のユーザーモデルを返す依存性関数"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """ユーザー名とパスワードでログインし、アクセストークンを取得する"""
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """新しいユーザーを作成する"""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user_data=user)

@app.get("/users/me", response_model=schemas.UserResponse, tags=["Users"])
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """現在ログインしているユーザーの情報を取得する"""
    return current_user

@app.put("/users/me/fcm_token", response_model=schemas.UserResponse, tags=["Users"])
def update_fcm_token_for_current_user(
    token_data: schemas.FCMTokenUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """現在ログインしているユーザーのFCMトークンを更新する"""
    return crud.update_user_fcm_token(db=db, user_id=current_user.id, fcm_token=token_data.fcm_token)


@app.post("/habits", response_model=schemas.HabitResponse, status_code=status.HTTP_201_CREATED, tags=["Habits"])
def create_habit(
    habit: schemas.HabitCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """新しい習慣を作成する"""
    return crud.create_habit(db, habit_data=habit, user_id=current_user.id)

@app.get("/habits", response_model=list[schemas.HabitResponse], tags=["Habits"])
def read_habits_for_user(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """ログインしているユーザーのすべての習慣を取得する"""
    return crud.get_habits_by_user(db=db, user_id=current_user.id)

@app.get("/habits/{habit_id}", response_model=schemas.HabitResponse, tags=["Habits"])
def read_habit(
    habit_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """IDで指定された単一の習慣を取得する"""
    habit = crud.get_habit(db, habit_id=habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit

@app.put("/habits/{habit_id}", response_model=schemas.HabitResponse, tags=["Habits"])
def update_habit(
    habit_id: int, 
    habit: schemas.HabitUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """IDで指定された習慣を更新する"""
    db_habit = crud.get_habit(db, habit_id=habit_id)
    if not db_habit or db_habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    return crud.update_habit(db, habit_id=habit_id, habit_data=habit)

@app.delete("/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Habits"])
def delete_habit(
    habit_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """IDで指定された習慣を削除する"""
    db_habit = crud.get_habit(db, habit_id=habit_id)
    if not db_habit or db_habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    crud.delete_habit(db, habit_id=habit_id)
    return None 


@app.post("/habit_records", response_model=schemas.HabitRecordResponse, status_code=status.HTTP_201_CREATED, tags=["Habit Records"])
def create_habit_record(
    record: schemas.HabitRecordCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """新しい習慣の記録を作成する"""
    db_habit = crud.get_habit(db, habit_id=record.habit_id)
    if not db_habit or db_habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found for this user")
        
    try:
        return crud.create_habit_record(db, record)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Record for this date already exists")

@app.get("/habits/{habit_id}/records", response_model=list[schemas.HabitRecordResponse], tags=["Habit Records"])
def read_habit_records_for_habit(
    habit_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """特定の習慣について、指定された期間の達成記録一覧を取得する"""
    db_habit = crud.get_habit(db, habit_id=habit_id)
    if not db_habit or db_habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return crud.get_habit_records_by_date_range(db=db, habit_id=habit_id, start_date=start_date, end_date=end_date)


@app.post("/habits/{habit_id}/goals", response_model=schemas.GoalResponse, status_code=status.HTTP_201_CREATED, tags=["Goals"])
def create_goal(
    habit_id: int,
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """特定の習慣に新しい目標を作成する"""
    db_habit = crud.get_habit(db, habit_id=habit_id)
    if not db_habit or db_habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    new_goal = crud.create_goal_for_habit(db=db, goal=goal, habit_id=habit_id)
    
    completed_records = crud.get_habit_records_by_date_range(db, habit_id=habit_id, start_date=new_goal.start_date, end_date=new_goal.end_date)
    unique_completed_dates = {rec.date for rec in completed_records if rec.status}
    current_count = len(unique_completed_dates)
    is_achieved = current_count >= new_goal.target_count

    return schemas.GoalResponse(
        id=new_goal.id,
        habit_id=new_goal.habit_id,
        target_count=new_goal.target_count,
        start_date=new_goal.start_date,
        end_date=new_goal.end_date,
        created_at=new_goal.created_at,
        current_count=current_count,
        is_achieved=is_achieved
    )

@app.get("/habits/{habit_id}/goals", response_model=list[schemas.GoalResponse], tags=["Goals"])
def read_goals(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """特定の習慣のすべての目標と、その達成状況を取得する"""
    db_habit = crud.get_habit(db, habit_id=habit_id)
    if not db_habit or db_habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")

    goals = crud.get_goals_for_habit(db, habit_id=habit_id)
    response_goals = []
    for goal in goals:
        completed_records = crud.get_habit_records_by_date_range(db, habit_id=habit_id, start_date=goal.start_date, end_date=goal.end_date)
        unique_completed_dates = {rec.date for rec in completed_records if rec.status}
        current_count = len(unique_completed_dates)
        is_achieved = current_count >= goal.target_count
        
        response_goals.append(schemas.GoalResponse(
            id=goal.id,
            habit_id=goal.habit_id,
            target_count=goal.target_count,
            start_date=goal.start_date,
            end_date=goal.end_date,
            created_at=goal.created_at,
            current_count=current_count,
            is_achieved=is_achieved
        ))
    return response_goals

@app.post("/notifications", response_model=schemas.NotificationResponse, status_code=status.HTTP_201_CREATED, tags=["Notifications"])
def create_notification(
    notification: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """新しい通知設定を作成する"""
    db_habit = crud.get_habit(db, habit_id=notification.habit_id)
    if not db_habit or db_habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found for this user")

    return crud.create_notification(db, notification=notification, user_id=current_user.id)

@app.get("/habits/{habit_id}/notifications", response_model=list[schemas.NotificationResponse], tags=["Notifications"])
def read_notifications_for_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """特定の習慣に紐づく通知設定をすべて取得する"""
    db_habit = crud.get_habit(db, habit_id=habit_id)
    if not db_habit or db_habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    return crud.get_notifications_for_habit(db, habit_id=habit_id) 

@app.put("/notifications/{notification_id}", response_model=schemas.NotificationResponse, tags=["Notifications"])
def update_notification(
    notification_id: int,
    notification_update: schemas.NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """IDで指定された通知設定を更新する"""
    db_notification = crud.get_notification(db, notification_id=notification_id)
    if not db_notification or db_notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    return crud.update_notification(db, notification_id=notification_id, notification_update=notification_update)

@app.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Notifications"])
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """IDで指定された通知設定を削除する"""
    db_notification = crud.get_notification(db, notification_id=notification_id)
    if not db_notification or db_notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    crud.delete_notification(db, notification_id=notification_id)
    return None
