from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas import HabitCreate, HabitResponse
from crud import create_habit
from models import Base
from database import engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.post("/habits/", response_model=HabitResponse)
async def add_habit(habit: HabitCreate, db: Session = Depends(get_db)):
    return create_habit(db, habit)