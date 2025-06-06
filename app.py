from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, crud, schemas
from sqlalchemy.exc import IntegrityError

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
def create_habit_record(record: schemas.HabitRecordCreate, db: Session = Depends(get_db)):
    return crud.create_habit_record(db, record)

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
