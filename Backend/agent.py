import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def groq_available():
    return bool(os.getenv("GROQ_API_KEY"))


def ask_groq(prompt: str, model: str = "llama-3.1-8b-instant"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful productivity assistant. Keep responses concise and practical."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


def classify_task(title: str):
    if groq_available():
        prompt = f"""
Classify this task:

Task: {title}

Return only valid JSON in this exact format:
{{
  "category": "work | personal | health | learning",
  "priority": "low | medium | high"
}}

Rules:
- category must be one of: work, personal, health, learning
- priority must be one of: low, medium, high
- urgent/deadline/today/submit/finish tasks should usually be high priority
"""

        try:
            result = ask_groq(prompt)
            data = json.loads(result)

            return {
                "category": data.get("category", "personal"),
                "priority": data.get("priority", "medium")
            }

        except Exception:
            pass

    text = title.lower()

    category = "personal"
    priority = "medium"

    health_keywords = ["gym", "workout", "exercise", "doctor", "medicine", "walk", "run"]
    learning_keywords = ["study", "revise", "learn", "course", "assignment", "project", "sql", "python", "fastapi"]
    work_keywords = ["client", "meeting", "report", "email", "office", "deadline", "presentation"]

    urgent_keywords = ["today", "urgent", "important", "deadline", "submit", "finish", "asap"]

    if any(word in text for word in health_keywords):
        category = "health"
    elif any(word in text for word in learning_keywords):
        category = "learning"
    elif any(word in text for word in work_keywords):
        category = "work"

    if any(word in text for word in urgent_keywords):
        priority = "high"

    return {
        "category": category,
        "priority": priority
    }


def generate_eod_summary(completed_tasks, slipped_tasks, evening_note):
    completed_titles = [task.title for task in completed_tasks]
    slipped_titles = [task.title for task in slipped_tasks]

    if groq_available():
        prompt = f"""
Write an end-of-day productivity summary.

Completed tasks:
{completed_titles}

Slipped tasks:
{slipped_titles}

User evening note:
{evening_note}

Return the response in this exact format:

Summary:
<one short paragraph>

Tomorrow Plan:
<short practical plan>
"""

        try:
            result = ask_groq(prompt, model="llama-3.3-70b-versatile")

            if "Tomorrow Plan:" in result:
                summary_part, plan_part = result.split("Tomorrow Plan:", 1)

                summary_text = summary_part.replace("Summary:", "").strip()
                tomorrow_plan = plan_part.strip()

                return summary_text, tomorrow_plan

            return result, "Review slipped tasks first tomorrow."

        except Exception:
            pass

    if completed_titles:
        completed_text = ", ".join(completed_titles)
    else:
        completed_text = "no planned tasks"

    if slipped_titles:
        slipped_text = ", ".join(slipped_titles)
    else:
        slipped_text = "nothing important slipped"

    summary = (
        f"Today you completed {completed_text}. "
        f"You still need to follow up on {slipped_text}. "
    )

    if evening_note:
        summary += f"Your note for the day was: {evening_note}"

    if slipped_titles:
        tomorrow_plan = (
            "Start tomorrow by finishing: "
            + ", ".join(slipped_titles)
            + ". Then continue with your next highest-priority tasks."
        )
    else:
        tomorrow_plan = (
            "Tomorrow, continue with your planned priorities and keep the same momentum."
        )

    return summary, tomorrow_plan


def generate_weekly_review(tasks):
    if not tasks:
        return "No tasks were found for this week. Start logging tasks daily to see weekly patterns."

    task_data = [
        {
            "title": task.title,
            "category": task.category,
            "priority": task.priority,
            "completed": task.completed,
            "due_date": str(task.due_date)
        }
        for task in tasks
    ]

    if groq_available():
        prompt = f"""
Analyze this user's weekly productivity pattern.

Tasks:
{json.dumps(task_data, indent=2)}

Write a short weekly review covering:
- total planned tasks
- completed vs slipped tasks
- dominant category
- one repeated pattern
- one practical suggestion for next week

Keep it to one paragraph.
"""

        try:
            return ask_groq(prompt, model="llama-3.3-70b-versatile")
        except Exception:
            pass

    total_tasks = len(tasks)
    completed_tasks = [task for task in tasks if task.completed]
    slipped_tasks = [task for task in tasks if not task.completed]

    category_counts = {}

    for task in tasks:
        category_counts[task.category] = category_counts.get(task.category, 0) + 1

    most_common_category = max(
        category_counts,
        key=category_counts.get
    )

    review = (
        f"This week you planned {total_tasks} tasks and completed "
        f"{len(completed_tasks)} of them. "
    )

    review += (
        f"Your most common task category was {most_common_category}. "
    )

    if slipped_tasks:
        slipped_titles = [task.title for task in slipped_tasks]
        review += (
            "The tasks that slipped were: "
            + ", ".join(slipped_titles)
            + ". "
        )

        slipped_categories = {}

        for task in slipped_tasks:
            slipped_categories[task.category] = slipped_categories.get(task.category, 0) + 1

        most_slipped_category = max(
            slipped_categories,
            key=slipped_categories.get
        )

        review += (
            f"You seem to be delaying {most_slipped_category} tasks the most. "
            "Next week, schedule those earlier in the day or reduce the number of tasks you plan."
        )
    else:
        review += (
            "Nothing slipped this week. Your planning was realistic and consistent."
        )

    return review