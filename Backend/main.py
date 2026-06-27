from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from Backend.auth import create_access_token, get_current_user

from Backend.database import Base, engine, get_db
from Backend import models, crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title = "Personal Productivity Agent",
    description="A daily productivity app with an AI agent for task tracking and planning.",
    version="1.0.0",
)

@app.get("/")
def home():
    return {
        "message":"Personal Productivity Agent API is running"
    }

@app.get("/health")
def health_check():
    return {
        "status":"ok"
    }

@app.post("/signup",response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate,db:Session = Depends(get_db)):
    exisitng_user = crud.get_user_by_email(db,user.email)

    if exisitng_user:
        raise HTTPException(
            status_code=400,
            details = "This email is already registered."
        )
    
    return crud.create_user(db,user)

@app.post("/login",response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db:Session = Depends(get_db)):
    user = crud.authenticate_user(
        db,
        user_data.email,
        user_data.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail = "Invalid email or password"

        )
    
    access_token = create_access_token(
        data={"sub":user.email}
    )

    return {
        "access_token" : access_token,
        "token_type" : "bearer"
    }

@app.get("/me",response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/tasks", response_model=schemas.TaskResponse)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_task(
        db=db,
        task=task,
        user_id=current_user.id
    )

@app.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_user_tasks(
        db=db,
        user_id=current_user.id
    )


@app.patch("/tasks/{task_id}/complete", response_model=schemas.TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task = crud.complete_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@app.get("/tasks/overdue", response_model=list[schemas.TaskResponse])
def get_overdue_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_overdue_tasks(
        db=db,
        user_id=current_user.id
    )


@app.post("/checkin/morning")
def morning_checkin(
    checkin: schemas.MorningCheckIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_morning_checkin(
        db=db,
        checkin=checkin,
        user_id=current_user.id
    )


@app.post("/checkin/evening")
def evening_checkin(
    checkin: schemas.EveningCheckIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_evening_checkin(
        db=db,
        checkin=checkin,
        user_id=current_user.id
    )


@app.post("/eod/run", response_model=schemas.EODResponse)
def run_eod(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.run_eod(
        db=db,
        user_id=current_user.id
    )

@app.post("/weekly-review/run", response_model=schemas.WeeklyReviewResponse)
def run_weekly_review(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.run_weekly_review(
        db=db,
        user_id=current_user.id
    )