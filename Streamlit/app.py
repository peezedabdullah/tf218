import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta, time

st.set_page_config("ORAICAN Project Tracker", layout="wide")

# Database connection
DB = "./Streamlit/oraican.db"

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Title TEXT,
        Description TEXT,
        Status TEXT,
        DueDate TEXT,
        Created TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Topic TEXT,
        Date TEXT,
        Time TEXT,
        Created TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper functions
def add_task(title, desc, status, due):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (Title, Description, Status, DueDate, Created)
        VALUES (?, ?, ?, ?, ?)
    """, (title, desc, status, due, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_tasks(start_date, end_date):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("""
        SELECT * FROM tasks
        WHERE DueDate BETWEEN ? AND ?
        ORDER BY DueDate
    """, conn, params=(start_date, end_date))
    conn.close()
    return df

def add_meeting(topic, date, time_val):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meetings (Topic, Date, Time, Created)
        VALUES (?, ?, ?, ?)
    """, (topic, date, time_val, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_meetings(start_date, end_date):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("""
        SELECT * FROM meetings
        WHERE Date BETWEEN ? AND ?
        ORDER BY Date, Time
    """, conn, params=(start_date, end_date))
    conn.close()
    return df

# UI
st.title("📊 ORAICAN Project Tracker")

tab1, tab2 = st.tabs(["📝 Tasks", "📅 Schedule"])

# WEEK RANGE CONTROL
if "week_offset" not in st.session_state:
    st.session_state.week_offset = 0

def get_week_range(offset):
    today = datetime.today() + timedelta(weeks=offset)
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start.date(), end.date()

start_date, end_date = get_week_range(st.session_state.week_offset)

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅️ Previous Week"):
        st.session_state.week_offset -= 1
with col2:
    st.write(f"### Viewing: {start_date} to {end_date}")
with col3:
    if st.button("Next Week ➡️"):
        st.session_state.week_offset += 1

with st.expander("📅 Or choose a custom date range"):
    start_date = st.date_input("Start", start_date)
    end_date = st.date_input("End", end_date)

# ---------------------------
# TASKS TAB
with tab1:
    st.subheader("Task Management")

    with st.expander("➕ Add New Task"):
        title = st.text_input("Task Title")
        desc = st.text_area("Description")
        status = st.selectbox("Status", ["To Do", "In Progress", "Done"])
        due = st.date_input("Due Date")
        if st.button("Add Task"):
            add_task(title, desc, status, due.strftime("%Y-%m-%d"))
            st.success("✅ Task added.")

    st.subheader("📋 Tasks This Week")
    tasks = get_tasks(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    if not tasks.empty:
        filter_status = st.selectbox("Filter by Status", ["All"] + tasks["Status"].unique().tolist())
        filtered = tasks if filter_status == "All" else tasks[tasks["Status"] == filter_status]
        st.dataframe(filtered.drop(columns=["id"]), use_container_width=True)
    else:
        st.info("No tasks in this range.")

# ---------------------------
# MEETINGS TAB
with tab2:
    st.subheader("Meeting Scheduler")

    with st.expander("📌 Schedule a Meeting"):
        topic = st.text_input("Meeting Topic")
        date = st.date_input("Meeting Date")
        time_val = st.time_input("Meeting Time", value=time(10, 0))
        if st.button("Add Meeting"):
            add_meeting(topic, date.strftime("%Y-%m-%d"), time_val.strftime("%H:%M"))
            st.success("📅 Meeting scheduled.")

    st.subheader("📆 Meetings This Week")
    meetings = get_meetings(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    if not meetings.empty:
        st.dataframe(meetings.drop(columns=["id"]), use_container_width=True)
    else:
        st.info("No meetings in this range.")
