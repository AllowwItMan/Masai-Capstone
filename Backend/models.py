from sqlalchemy import Boolean, Column, ForeignKey, DateTime, Integer, String, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from Backend.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("Task", back_populates="owner")
    daily_logs = relationship("DailyLog",back_populates="owner")
    eod_summaries = relationship("EODSummary",back_populates="owner")
    weekly_reviews = relationship("WeeklyReview",back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String,nullable=False)
    category = Column(String,default="personal")
    priority = Column(String,default="medium")
    due_date = Column(Date, nullable=True)
    completed = Column(Boolean,default=False)
    completed_at = Column(DateTime,nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="tasks")

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer,primary_key=True,index=True)
    log_date = Column(Date,nullable=False)
    morning_note = Column(Text,nullable=True)
    evening_note = Column(Text, nullable=True)
    created_at = Column(DateTime,default=datetime.utcnow)

    user_id = Column(Integer,ForeignKey("users.id"))

    owner = relationship("User", back_populates="daily_logs")

class EODSummary(Base):
    __tablename__ = "eod_summaries"
    id = Column(Integer, primary_key=True, index=True)
    summary_date = Column(Date, nullable=False)
    summary_text = Column(Text, nullable=False)
    tomorrow_plan = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="eod_summaries")


class WeeklyReview(Base):
    __tablename__ = "weekly_reviews"

    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False)
    review_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="weekly_reviews")


