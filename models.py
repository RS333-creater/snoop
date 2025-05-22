from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, TIMESTAMP, Time, Text
from sqlalchemy.orm import relationship
from database import Base  

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    habits = relationship("Habit", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False)
    user = relationship("User", back_populates="habits")
    habit_records = relationship("HabitRecord", back_populates="habit")
    notifications = relationship("Notification", back_populates="habit")

class HabitRecord(Base):
    __tablename__ = "habit_records"
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(Boolean, nullable=False, default=False)
    habit = relationship("Habit", back_populates="habit_records")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    time = Column(Time, nullable=False)
    enabled = Column(Boolean, default=True)
    user = relationship("User", back_populates="notifications")
    habit = relationship("Habit", back_populates="notifications")