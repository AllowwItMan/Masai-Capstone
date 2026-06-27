import requests
import streamlit as st

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Personal Productivity Agent",
    layout="wide"
)

if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None


def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def signup(name, email, password):
    response = requests.post(
        f"{API_URL}/signup",
        json={
            "name": name,
            "email": email,
            "password": password
        }
    )
    return response


def login(email, password):
    response = requests.post(
        f"{API_URL}/login",
        json={
            "email": email,
            "password": password
        }
    )

    if response.status_code == 200:
        data = response.json()
        st.session_state.token = data["access_token"]

        me_response = requests.get(
            f"{API_URL}/me",
            headers=auth_headers()
        )

        if me_response.status_code == 200:
            st.session_state.user = me_response.json()

    return response


def get_tasks():
    response = requests.get(
        f"{API_URL}/tasks",
        headers=auth_headers()
    )

    if response.status_code == 200:
        return response.json()

    return []


def create_task(title, due_date):
    response = requests.post(
        f"{API_URL}/tasks",
        headers=auth_headers(),
        json={
            "title": title,
            "due_date": str(due_date)
        }
    )
    return response


def complete_task(task_id):
    response = requests.patch(
        f"{API_URL}/tasks/{task_id}/complete",
        headers=auth_headers()
    )
    return response


def morning_checkin(morning_note, tasks):
    response = requests.post(
        f"{API_URL}/checkin/morning",
        headers=auth_headers(),
        json={
            "morning_note": morning_note,
            "tasks": tasks
        }
    )
    return response


def evening_checkin(evening_note, completed_task_ids):
    response = requests.post(
        f"{API_URL}/checkin/evening",
        headers=auth_headers(),
        json={
            "evening_note": evening_note,
            "completed_task_ids": completed_task_ids
        }
    )
    return response


def run_eod():
    response = requests.post(
        f"{API_URL}/eod/run",
        headers=auth_headers()
    )
    return response

def run_weekly_review():
    response = requests.post(
        f"{API_URL}/weekly-review/run",
        headers=auth_headers()
    )
    return response


st.title("Personal Productivity Agent")

if not st.session_state.token:
    tab_login, tab_signup = st.tabs(["Login", "Signup"])

    with tab_login:
        st.subheader("Login")

        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            response = login(login_email, login_password)

            if response.status_code == 200:
                st.success("Logged in successfully")
                st.rerun()
            else:
                st.error("Invalid email or password")

    with tab_signup:
        st.subheader("Create account")

        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Signup"):
            response = signup(name, email, password)

            if response.status_code == 200:
                st.success("Account created. Please login.")
            else:
                st.error(response.json().get("detail", "Signup failed"))

else:
    user = st.session_state.user

    st.sidebar.success(f"Logged in as {user['name']}")

    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

    page = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Morning Check-in",
        "Evening Check-in",
        "Run EOD",
        "Weekly Review"
    ]
)    

    if page == "Dashboard":
        st.subheader("Your Tasks")

        with st.form("add_task_form"):
            task_title = st.text_input("New task")
            due_date = st.date_input("Due date")
            submitted = st.form_submit_button("Add task")

            if submitted:
                if task_title.strip():
                    response = create_task(task_title, due_date)

                    if response.status_code == 200:
                        st.success("Task added")
                        st.rerun()
                    else:
                        st.error("Could not add task")
                        st.error(f"Request method: {response.request.method}")
                        st.error(f"URL: {response.url}")
                        st.error(f"Status: {response.status_code}")
                        st.error(response.text)

        tasks = get_tasks()

        if not tasks:
            st.info("No tasks yet.")
        else:
            for task in tasks:
                col1, col2, col3, col4, col5 = st.columns([4, 2, 2, 2, 2])

                with col1:
                    status = "✅" if task["completed"] else "⬜"
                    st.write(f"{status} {task['title']}")

                with col2:
                    st.write(task["category"])

                with col3:
                    st.write(task["priority"])

                with col4:
                    st.write(task["due_date"])

                with col5:
                    if not task["completed"]:
                        if st.button("Complete", key=f"complete_{task['id']}"):
                            complete_task(task["id"])
                            st.rerun()

    elif page == "Morning Check-in":
        st.subheader("Morning Check-in")

        morning_note = st.text_area(
            "What are you planning today?"
        )

        task_lines = st.text_area(
            "Write tasks, one per line"
        )

        if st.button("Submit Morning Check-in"):
            tasks = []

            for line in task_lines.split("\n"):
                clean_line = line.strip()

                if clean_line:
                    tasks.append({
                        "title": clean_line
                    })

            response = morning_checkin(morning_note, tasks)

            if response.status_code == 200:
                st.success("Morning check-in saved")
            else:
                st.error("Could not save morning check-in")

    elif page == "Evening Check-in":
        st.subheader("Evening Check-in")

        tasks = get_tasks()
        incomplete_tasks = [
            task for task in tasks
            if not task["completed"]
        ]

        evening_note = st.text_area(
            "What did you actually complete today?"
        )

        completed_ids = []

        for task in incomplete_tasks:
            checked = st.checkbox(
                task["title"],
                key=f"evening_task_{task['id']}"
            )

            if checked:
                completed_ids.append(task["id"])

        if st.button("Submit Evening Check-in"):
            response = evening_checkin(evening_note, completed_ids)

            if response.status_code == 200:
                st.success("Evening check-in saved")
            else:
                st.error("Could not save evening check-in")

    elif page == "Run EOD":
        st.subheader("End-of-Day Summary")

        if st.button("Run My EOD"):
            response = run_eod()

            if response.status_code == 200:
                data = response.json()

                st.success("EOD summary generated")

                st.markdown("### Summary")
                st.write(data["summary_text"])

                st.markdown("### Tomorrow's Plan")
                st.write(data["tomorrow_plan"])
            else:
                st.error("Could not generate EOD summary")

    
    elif page == "Weekly Review":
        st.subheader("Weekly Review")

        if st.button("Run Weekly Review"):
            response = run_weekly_review()

            if response.status_code == 200:
                data = response.json()

                st.success("Weekly review generated")

                st.write(f"Week: {data['week_start']} to {data['week_end']}")

                st.markdown("### Pattern Summary")
                st.write(data["review_text"])
            else:
                st.error("Could not generate weekly review")