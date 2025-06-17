from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, crud, schemas, security
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, date

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    トークンを検証し、現在のユーザーモデルを返す依存性関数
    """
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

@app.post("/habits", response_model=schemas.HabitResponse)
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(get_db)):
    fake_user_id = 1
    return crud.create_habit(db, habit, user_id=fake_user_id)

@app.get("/habits/{habit_id}", response_model=schemas.HabitResponse)
def read_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = crud.get_habit(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit

@app.get("/habits", response_model=list[schemas.HabitResponse])
def read_habits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    habits = crud.get_habits(db, skip=skip, limit=limit)
    return habits

@app.put("/habits/{habit_id}", response_model=schemas.HabitResponse)
def update_habit(habit_id: int, habit: schemas.HabitUpdate, db: Session = Depends(get_db)):
    updated_habit = crud.update_habit(db, habit_id, habit)
    if not updated_habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return updated_habit

@app.delete("/habits/{habit_id}", response_model=schemas.HabitResponse)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    deleted_habit = crud.delete_habit(db, habit_id)
    if not deleted_habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return deleted_habit

@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_user(db, user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    
@app.get("/users", response_model=list[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}", response_model=schemas.UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted_user = crud.delete_user(db, user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user

@app.post("/habit_records", response_model=schemas.HabitRecordResponse)
def create_habit_record(record: schemas.HabitRecordCreate, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    db_habit = crud.get_habit(db, habit_id=record.habit_id)
    if not db_habit or db_habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    try:
        return crud.create_habit_record(db, record)
    except IntegrityError: # データベースのユニーク制約違反エラーをキャッチ
        db.rollback()
        raise HTTPException(status_code=409, detail="Record for this date already exists")

@app.get("/habit_records/{record_id}", response_model=schemas.HabitRecordResponse)
def read_habit_record(record_id: int, db: Session = Depends(get_db)):
    record = crud.get_habit_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="HabitRecord not found")
    return record

@app.get("/habit_records", response_model=list[schemas.HabitRecordResponse])
def read_habit_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_habit_records(db, skip=skip, limit=limit)

@app.put("/habit_records/{record_id}", response_model=schemas.HabitRecordResponse)
def update_habit_record(record_id: int, record: schemas.HabitRecordUpdate, db: Session = Depends(get_db)):
    updated = crud.update_habit_record(db, record_id, record)
    if not updated:
        raise HTTPException(status_code=404, detail="HabitRecord not found")
    return updated

@app.delete("/habit_records/{record_id}", response_model=schemas.HabitRecordResponse)
def delete_habit_record(record_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_habit_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="HabitRecord not found")
    return deleted

@app.get("/habits/{habit_id}/records", response_model=list[schemas.HabitRecordResponse])
def read_habit_records_for_habit(
    habit_id: int,
    start_date: date, # 例: 2025-06-01
    end_date: date,   # 例: 2025-06-30
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    特定の習慣について、指定された期間の達成記録一覧を取得する
    """
    # まず、リクエストされた習慣が存在し、かつ現在のユーザーのものであるかを確認する
    habit = crud.get_habit(db, habit_id=habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    # 所有者であることが確認できたら、指定期間の記録を取得する
    records = crud.get_habit_records_by_date_range(
        db=db, habit_id=habit_id, start_date=start_date, end_date=end_date
    )
    return records

@app.post("/notifications", response_model=schemas.NotificationResponse)
def create_notification(notification: schemas.NotificationCreate, db: Session = Depends(get_db)):
    return crud.create_notification(db, notification)

@app.get("/notifications/{notification_id}", response_model=schemas.NotificationResponse)
def read_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = crud.get_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@app.get("/notifications", response_model=list[schemas.NotificationResponse])
def read_notifications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_notifications(db, skip=skip, limit=limit)

@app.put("/notifications/{notification_id}", response_model=schemas.NotificationResponse)
def update_notification(notification_id: int, notification: schemas.NotificationUpdate, db: Session = Depends(get_db)):
    updated = crud.update_notification(db, notification_id, notification)
    if not updated:
        raise HTTPException(status_code=404, detail="Notification not found")
    return updated

@app.delete("/notifications/{notification_id}", response_model=schemas.NotificationResponse)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_notification(db, notification_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    return deleted

# --- エンドポイント ---

# 1. ログイン用のエンドポイントを新設
@app.post("/token", response_model=schemas.Token) # Tokenスキーマをschemas.pyに追加する必要あり
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
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

# 2. 既存のcreate_habitを修正（ここがゴール！）
@app.post("/habits", response_model=schemas.HabitResponse)
def create_habit(
    habit: schemas.HabitCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # ★ 依存関係として現在のユーザーを取得
):
    # ★ fake_user_id の代わりに、認証済みユーザーのIDを使う！
    return crud.create_habit(db, habit=habit, user_id=current_user.id)

@app.post("/habits/{habit_id}/goals", response_model=schemas.GoalResponse)
def create_goal(
    habit_id: int,
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """特定の習慣に新しい目標を作成する"""
    # 習慣の所有者か確認
    db_habit = crud.get_habit(db, habit_id=habit_id)
    if not db_habit or db_habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    # 目標を作成
    new_goal = crud.create_goal_for_habit(db=db, goal=goal, habit_id=habit_id)
    
    # 作成した目標の現在の達成状況を計算してレスポンスを組み立てる
    completed_records = [
        record for record in new_goal.habit.habit_records
        if record.status and new_goal.start_date <= record.date <= new_goal.end_date
    ]
    current_count = len(completed_records)
    is_achieved = current_count >= new_goal.target_count

    return schemas.GoalResponse(
        **new_goal.__dict__,
        current_count=current_count,
        is_achieved=is_achieved
    )

@app.get("/habits/{habit_id}/goals", response_model=list[schemas.GoalResponse])
def read_goals(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """特定の習慣のすべての目標と、その達成状況を取得する"""
    # 習慣の所有者か確認
    db_habit = crud.get_habit(db, habit_id=habit_id)
    if not db_habit or db_habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")

    # データベースから目標の一覧を取得
    goals = crud.get_goals_for_habit(db, habit_id=habit_id)
    
    # 各目標の達成状況を計算して、レスポンス用のリストを作成
    response_goals = []
    for goal in goals:
        # 期間内の完了した記録をフィルタリング
        completed_records = [
            record for record in goal.habit.habit_records
            if record.status and goal.start_date <= record.date <= goal.end_date
        ]
        unique_completed_dates = {record.date for record in completed_records}
        current_count = len(unique_completed_dates) 
        is_achieved = current_count >= goal.target_count
        
        response_goals.append(schemas.GoalResponse(
            **goal.__dict__,
            current_count=current_count,
            is_achieved=is_achieved
        ))
        
    return response_goals

@app.delete("/goals/{goal_id}", status_code=204)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """IDで指定された目標を削除する"""
    # 削除対象の目標を取得
    db_goal = crud.get_goal(db, goal_id=goal_id)
    
    # 目標が存在し、かつその親である習慣が現在のユーザーのものであるか確認
    if not db_goal or db_goal.habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    crud.delete_goal(db, goal_id=goal_id)
    return {"detail": "Goal deleted successfully"} # 204 No Content なので実際には返らない