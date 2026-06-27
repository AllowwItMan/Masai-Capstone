# Personal Productivity Agent

A daily productivity tracker powered by an AI assistant. The app helps users plan their day, track completed work, surface overdue tasks, generate end-of-day summaries, and review weekly productivity patterns.

## Problem Statement

Most people do not have a productivity problem. They have a memory and prioritization problem. They forget what was due, underestimate how long things take, and end the day unsure whether they completed the important work.

This project solves that by giving the user a daily check-in workflow and an AI agent that remembers their task history, detects slipped tasks, summarizes the day, and suggests what to do next.

## Features

- User signup and login with JWT authentication
- Morning check-in with planned tasks
- Automatic task classification using Groq LLM
- Task categories: work, personal, health, learning
- Task priority tagging: low, medium, high
- Task dashboard
- Mark tasks as completed
- Overdue task detection
- Evening check-in
- End-of-day summary generation
- Tomorrow plan suggestion
- Weekly productivity review
- SQLite database storage
- Streamlit frontend
- FastAPI backend

## Tech Stack

### Frontend
- Streamlit

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- JWT authentication

### AI
- Groq API
- Llama 3.1 8B for task classification
- Llama 3.3 70B for summaries and planning

## Project Structure

```text
Capstone_MASAI/
  backend/
    main.py
    database.py
    models.py
    schemas.py
    auth.py
    crud.py
    agent.py

  frontend/
    app.py

  productivity.db
  requirements.txt
  .env.example
  README.md
```


## Setup Instructions

### 1. Open the project folder

cd Capstone_MASAI

### 2. Install dependencies

pip install -r requirements.txt

### 3. Add environment variables

Create a `.env` file and add:

GROQ_API_KEY=your_groq_api_key_here

### 4. Start backend

uvicorn backend.main:app --reload

The Backend runs at : " http://127.0.0.1:8000 "

API Docs : " http://127.0.0.1:8000/docs "

### 5. Start frontend

Open a second terminal

streamlit run frontend/app.py

The Frontend runs at : " http://localhost:8501 "


## Main Workflow

1. User signs up and logs in.

2. User completes morning check-in by entering planned tasks.

3. Agent classifies tasks by category and priority.

4. User completes some rasks during the day.

5. User completes evening check-in.

6. User clicks "Run my EOD".

7. Agent generat    - completed task sumamry
    - slipped task summary
    - tomorrow's suggested plan

8. User can run weekly review to identify patterns.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API home route |
| GET | `/health` | Health check |
| POST | `/signup` | Create a new user account |
| POST | `/login` | Login and receive JWT access token |
| GET | `/me` | Get logged-in user details |
| POST | `/tasks` | Create a task |
| GET | `/tasks` | Get all tasks for the logged-in user |
| PATCH | `/tasks/{task_id}/complete` | Mark a task as completed |
| GET | `/tasks/overdue` | Get overdue incomplete tasks |
| POST | `/checkin/morning` | Save morning check-in and planned tasks |
| POST | `/checkin/evening` | Save evening check-in and completed tasks |
| POST | `/eod/run` | Generate end-of-day summary |
| POST | `/weekly-review/run` | Generate weekly productivity review |


## Database Tables

 - users

 - tasks

 - daily_logs

 - eod_summaries

 - weekly_reviews


## AI Agent Responsibilities 

The agent performs four main jobs:

1. Classifies taks into productivity categories.

2. Detects priority based on task language.

3. Generates end-of-day summaries.

4. Finds weekly productivity patterns.


## Future Improvements 

 - Browser speech-to-text for voice morning cehck-in.

 - Google calender import.

 - Email reminders for overdue tasks.

 - Streak tracking.

## Author
 
### Abhigyan Anand
### ID - 

## Project Status

### Core features completed. The app supports authentication, task management, daily check-ins, AI classification, EOD summaries, and weekly reviews.

## Demo Script

1. Start the FastAPI backend.
2. Start the Streamlit frontend.
3. Sign up or log in as a user.
4. Add a few tasks:
   - Submit capstone report today
   - Go to gym
   - Revise SQL joins
5. Show that the agent automatically classifies the tasks.
6. Mark one or two tasks as completed.
7. Submit the evening check-in.
8. Click Run My EOD.
9. Show the generated summary and tomorrow's plan.
10. Click Run Weekly Review.
11. Explain the weekly pattern summary.

