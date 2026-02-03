import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# ────────────────────────────────────────────────
# Config
# ────────────────────────────────────────────────
API_BASE = "http://127.0.0.1:8000"

# ────────────────────────────────────────────────
# Development auto-login (remove or comment out later)
# ────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state["user_id"] = 1          # ← put your real user_id here
    st.info("Development mode: auto-logged in as user ID 1")

if "user_id" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

user_id = st.session_state["user_id"]

# Sidebar with logout
with st.sidebar:
    st.write(f"Logged in as user ID: {user_id}")
    
    if st.button("Log out", type="secondary", use_container_width=True):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Optional: redirect to login page
        st.switch_page("app.py")   # or "app.py" if login is there
        
        # Force rerun so changes take effect immediately
        st.rerun()

st.title("Study Dashboard")
st.caption(f"User ID: {user_id}")

# ────────────────────────────────────────────────
# Add new session
# ────────────────────────────────────────────────
st.subheader("Log new study session")

with st.form("new_session_form", clear_on_submit=True):
    col1, col2 = st.columns([1, 1])

    with col1:
        subject_id = st.number_input(
            "Subject ID",
            min_value=1,
            step=1,
            value=1,
            help="You can later replace this with subject names"
        )

    with col2:
        duration = st.number_input(
            "Duration (minutes)",
            min_value=5,
            step=5,
            value=30
        )

    notes = st.text_area("Notes", height=100, placeholder="What did you study / how did it go?")

    submitted = st.form_submit_button("Save session", type="primary", use_container_width=True)

    if submitted:
        if duration < 1:
            st.error("Duration must be at least 1 minute.")
        else:
            try:
                r = requests.post(
                    f"{API_BASE}/study",
                    json={
                        "user_id": user_id,
                        "subject": subject_id,
                        "duration": duration,
                        "notes": notes.strip() or None
                    },
                    headers={"X-User-Id": str(user_id)}
                )

                if r.status_code == 200:
                    st.success("Session saved!")
                    st.rerun()  # refresh to show new row
                else:
                    try:
                        detail = r.json().get("detail", "Unknown error")
                        st.error(detail)
                    except:
                        st.error(f"Server responded with status {r.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the API: {e}")

# ────────────────────────────────────────────────
# Show existing sessions
# ────────────────────────────────────────────────
st.subheader("Your recent study sessions")

try:
    r = requests.get(
        f"{API_BASE}/study",
        headers={"X-User-Id": str(user_id)}
    )

    if r.status_code == 200:
        data = r.json()
        sessions = data.get("sessions", [])

        if sessions:
            # Prepare DataFrame
            df = pd.DataFrame(sessions)
            df["session_date"] = pd.to_datetime(df["session_date"])
            df = df.sort_values("session_date", ascending=False)

            # Optional formatting
            df["duration"] = df["duration"].astype(int).astype(str) + " min"
            df["notes"] = df["notes"].fillna("-")

            # Show table
            st.dataframe(
                df[["session_date", "subject_id", "duration", "notes"]],
                hide_index=True,
                column_config={
                    "session_date": st.column_config.DateColumn("Date", format="DD.MM.YYYY HH:mm"),
                    "subject_id": st.column_config.NumberColumn("Subject", format="%d"),
                    "duration": st.column_config.TextColumn("Duration"),
                    "notes": st.column_config.TextColumn("Notes")
                },
                use_container_width=True
            )

            # Quick stats
            total_min = df["duration"].str.extract(r'(\d+)').astype(int).sum().values[0]
            session_count = len(df)
            last_session = df["session_date"].max().strftime("%d.%m.%Y %H:%M")

            cols = st.columns(3)
            cols[0].metric("Total time", f"{total_min} min")
            cols[1].metric("Sessions", session_count)
            cols[2].metric("Last session", last_session)

        else:
            st.info("No study sessions yet. Add your first one above.")
    else:
        st.error(f"Could not load sessions (status {r.status_code})")

except Exception as e:
    st.error(f"Connection or data error: {e}")

# ────────────────────────────────────────────────
# Visualization - Charts
# ────────────────────────────────────────────────
st.subheader("Progress Charts")

if sessions:
    df = pd.DataFrame(sessions)
    df["session_date"] = pd.to_datetime(df["session_date"])

    # 1. Bar chart: total time per subject
    time_by_subject = df.groupby("subject_id")["duration"].sum().reset_index()
    time_by_subject["subject_id"] = "Subject " + time_by_subject["subject_id"].astype(str)

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.bar(time_by_subject["subject_id"], time_by_subject["duration"], color="#4CAF50")
    ax1.set_title("Total Study Time per Subject")
    ax1.set_xlabel("Subject")
    ax1.set_ylabel("Minutes")
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

    # 2. Line chart: study time over time
    daily = df.groupby(df["session_date"].dt.date)["duration"].sum().reset_index()
    daily["session_date"] = pd.to_datetime(daily["session_date"])

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.plot(daily["session_date"], daily["duration"], marker="o", color="#2196F3")
    ax2.set_title("Daily Study Time")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Minutes")
    ax2.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig2)

else:
    st.info("Add more sessions to see charts.")