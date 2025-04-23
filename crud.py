from sqlalchemy.orm import Session
from models import Habit
from schemas import HabitCreate
from datetime import datetime ,timezone
def create_habit(db: Session, habit_data: HabitCreate):
    new_habit = Habit(
        name=habit_data.name,
        description=habit_data.description,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit