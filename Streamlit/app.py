import streamlit as st
import pandas as pd
from datetime import datetime, time
import os

st.set_page_config("ORAICAN Project Tracker", layout="wide")

# ---------------------------
# File paths
TASKS_FILE = "tasks.csv"
MEETINGS_FILE = "meetings.csv"

# ---------------------------
# Helper functions
def load_csv(file, cols):
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file)

def save_csv(df, file):
    df.to_csv(file, index=False)

# ---------------------------
# Load data
tasks = load_csv(TASKS_FILE, ["Title", "Description", "Status", "Due Date", "Created"])
meetings = load_csv(MEETINGS_FILE, ["Topic", "Date", "Time", "Created"])

# ---------------------------
st.title("📊 ORAICAN Project Tracker")

tab1, tab2 = st.tabs(["📝 Tasks", "📅 Schedule"])

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
            new_task = pd.DataFrame([{
                "Title": title,
                "Description": desc,
                "Status": status,
                "Due Date": due.strftime("%Y-%m-%d"),
                "Created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            tasks = pd.concat([tasks, new_task], ignore_index=True)
            save_csv(tasks, TASKS_FILE)
            st.success("✅ Task added.")

    st.subheader("📋 Current Tasks")
    if not tasks.empty:
        filter_status = st.selectbox("Filter by Status", ["All"] + tasks["Status"].unique().tolist())
        filtered = tasks if filter_status == "All" else tasks[tasks["Status"] == filter_status]
        st.dataframe(filtered, use_container_width=True)
    else:
        st.info("No tasks yet. Add one above.")

# ---------------------------
# SCHEDULE TAB
with tab2:
    st.subheader("Meeting Scheduler")

    with st.expander("📅 Schedule a Discussion"):
        topic = st.text_input("Meeting Topic")
        date = st.date_input("Meeting Date")
        time_val = st.time_input("Meeting Time", value=time(10, 0))
        if st.button("Add Meeting"):
            new_meeting = pd.DataFrame([{
                "Topic": topic,
                "Date": date.strftime("%Y-%m-%d"),
                "Time": time_val.strftime("%H:%M"),
                "Created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            meetings = pd.concat([meetings, new_meeting], ignore_index=True)
            save_csv(meetings, MEETINGS_FILE)
            st.success("📌 Meeting added.")

    st.subheader("📆 Upcoming Meetings")
    if not meetings.empty:
        upcoming = meetings.sort_values(by=["Date", "Time"])
        st.dataframe(upcoming, use_container_width=True)
    else:
        st.info("No meetings scheduled yet.")

