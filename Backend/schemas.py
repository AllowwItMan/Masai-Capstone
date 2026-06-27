from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

from typing import List

class UserCreate(BaseModel):
    name : str
    email : EmailStr
    password : str

class UserLogin(BaseModel):
    email : EmailStr
    password : str

class UserResponse(BaseModel):
    id : int
    name : str
    email : EmailStr

    class config:
        from_attributes = True

class Token(BaseModel):
    access_token : str
    token_type : str


class TaskCreate(BaseModel):
    title: str
    category: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    category: str
    priority: str
    due_date: Optional[date]
    completed: bool

    class config:
        from_attributes = True



class MorningCheckIn(BaseModel):
    morning_note: str
    tasks: List[TaskCreate]


class DailyLogResponse(BaseModel):
    id: int
    log_date: date
    morning_note: Optional[str]
    evening_note: Optional[str]

    class Config:
        from_attributes = True


class EveningCheckIn(BaseModel):
    evening_note: str
    completed_task_ids: List[int]

class EODResponse(BaseModel):
    id: int
    summary_date: date
    summary_text: str
    tomorrow_plan: Optional[str]

    class Config:
        from_attributes = True


class WeeklyReviewResponse(BaseModel):
    id: int
    week_start: date
    week_end: date
    review_text: str

    class Config:
        from_attributes = True