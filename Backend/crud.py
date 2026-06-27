from sqlalchemy.orm import Session

from Backend import models, schemas
from Backend.auth import hash_password, verify_password
from datetime import date, datetime, timedelta

# from Backend.agent import generate_eod_summary
# from Backend.agent import generate_eod_summary, classify_task
from Backend.agent import generate_eod_summary, classify_task, generate_weekly_review

def get_user_by_email(db:Session,email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user:schemas.UserCreate):
    hashed_password = hash_password(user.password)

    db_user = models.User(
        name = user.name,
        email = user.email,
        hashed_password = hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def authenticate_user(db:Session, email:str, password:str):
    user = get_user_by_email(db,email)

    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    classification = classify_task(task.title)

    db_task = models.Task(
        title=task.title,
        category=task.category or classification["category"],
        priority=task.priority or classification["priority"],
        due_date=task.due_date,
        user_id=user_id
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

def get_user_tasks(db:Session, user_id:int):
    return db.query(models.Task).filter(
        models.Task.user_id == user_id
    ).all()


def complete_task(db: Session, task_id: int, user_id: int):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == user_id
    ).first()

    if not task:
        return None

    task.completed = True
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


def get_overdue_tasks(db: Session, user_id: int):
    today = date.today()

    return db.query(models.Task).filter(
        models.Task.user_id == user_id,
        models.Task.completed == False,
        models.Task.due_date < today
    ).all()


def create_morning_checkin(db: Session, checkin: schemas.MorningCheckIn, user_id: int):
    today = date.today()

    daily_log = models.DailyLog(
        log_date=today,
        morning_note=checkin.morning_note,
        user_id=user_id
    )

    db.add(daily_log)

    created_tasks = []

    for task in checkin.tasks:
        classification = classify_task(task.title)
        db_task = models.Task(
            title=task.title,
            category=task.category or classification["category"],
            priority=task.priority or classification["priority"],
            due_date=task.due_date or today,
            user_id=user_id
        )

        db.add(db_task)
        created_tasks.append(db_task)

    db.commit()
    db.refresh(daily_log)

    for task in created_tasks:
        db.refresh(task)

    return {
        "daily_log": daily_log,
        "tasks": created_tasks
    }


def create_evening_checkin(db: Session, checkin: schemas.EveningCheckIn, user_id: int):
    today = date.today()

    daily_log = db.query(models.DailyLog).filter(
        models.DailyLog.user_id == user_id,
        models.DailyLog.log_date == today
    ).first()

    if not daily_log:
        daily_log = models.DailyLog(
            log_date=today,
            user_id=user_id
        )
        db.add(daily_log)

    daily_log.evening_note = checkin.evening_note

    completed_tasks = []

    for task_id in checkin.completed_task_ids:
        task = db.query(models.Task).filter(
            models.Task.id == task_id,
            models.Task.user_id == user_id
        ).first()

        if task:
            task.completed = True
            task.completed_at = datetime.utcnow()
            completed_tasks.append(task)

    db.commit()
    db.refresh(daily_log)

    for task in completed_tasks:
        db.refresh(task)

    return {
        "daily_log": daily_log,
        "completed_tasks": completed_tasks
    }


def run_eod(db: Session, user_id: int):
    today = date.today()

    daily_log = db.query(models.DailyLog).filter(
        models.DailyLog.user_id == user_id,
        models.DailyLog.log_date == today
    ).first()

    evening_note = daily_log.evening_note if daily_log else ""

    todays_tasks = db.query(models.Task).filter(
        models.Task.user_id == user_id,
        models.Task.due_date == today
    ).all()

    completed_tasks = [
        task for task in todays_tasks
        if task.completed
    ]

    slipped_tasks = [
        task for task in todays_tasks
        if not task.completed
    ]

    summary_text, tomorrow_plan = generate_eod_summary(
        completed_tasks=completed_tasks,
        slipped_tasks=slipped_tasks,
        evening_note=evening_note
    )

    eod_summary = models.EODSummary(
        summary_date=today,
        summary_text=summary_text,
        tomorrow_plan=tomorrow_plan,
        user_id=user_id
    )

    db.add(eod_summary)
    db.commit()
    db.refresh(eod_summary)

    return eod_summary


def run_weekly_review(db: Session, user_id: int):
    today = date.today()
    week_start = today - timedelta(days=6)
    week_end = today

    tasks = db.query(models.Task).filter(
        models.Task.user_id == user_id,
        models.Task.due_date >= week_start,
        models.Task.due_date <= week_end
    ).all()

    review_text = generate_weekly_review(tasks)

    weekly_review = models.WeeklyReview(
        week_start=week_start,
        week_end=week_end,
        review_text=review_text,
        user_id=user_id
    )

    db.add(weekly_review)
    db.commit()
    db.refresh(weekly_review)

    return weekly_review