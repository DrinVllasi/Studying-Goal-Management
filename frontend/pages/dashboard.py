import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_BASE = "http://127.0.0.1:8000"

# ────────────────────────────────────────────────
# Auto-login for development (remove later)
# ────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state["user_id"] = 1  # ← change to your preferred test user ID
    st.info("Development mode: auto-logged in as user ID 1")

if "user_id" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

user_id = st.session_state["user_id"]

# ────────────────────────────────────────────────
# Sidebar with logout
# ────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**Logged in** as User ID: {user_id}")

    if st.button("Log out", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("app.py")  # ← adjust if login is named differently
        st.rerun()

st.title("Study Dashboard")
st.caption(f"User ID: {user_id}")

# ────────────────────────────────────────────────
# Add new study session form
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
                        "subject_id": subject_id,
                        "duration": duration,
                        "notes": notes.strip() or None
                    },
                    headers={"X-User-Id": str(user_id)}
                )

                if r.status_code == 200:
                    st.success("Session saved!")
                    st.rerun()
                else:
                    try:
                        detail = r.json()
                        st.error(str(detail))
                    except:
                        st.error(f"Server error ({r.status_code}): {r.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the API: {e}")

# ────────────────────────────────────────────────
# Fetch sessions
# ────────────────────────────────────────────────
sessions = []

try:
    r = requests.get(
        f"{API_BASE}/study",
        headers={"X-User-Id": str(user_id)}
    )

    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            sessions = data
        elif isinstance(data, dict) and "sessions" in data:
            sessions = data["sessions"]
        else:
            st.error("Unexpected response format from server")
    else:
        st.error(f"Could not load sessions (status {r.status_code}): {r.text}")

except Exception as e:
    st.error(f"Connection or data error: {e}")

# ────────────────────────────────────────────────
# Display table, stats, charts — no raw data anywhere
# ────────────────────────────────────────────────
if sessions:
    df = pd.DataFrame(sessions)
    df["session_date"] = pd.to_datetime(df["session_date"])
    df = df.sort_values("session_date", ascending=False)

    # Formatted display copy
    df_display = df.copy()
    df_display["duration"] = df_display["duration"].astype(int).astype(str) + " min"
    df_display["notes"] = df_display["notes"].fillna("-")

    # Table
    st.dataframe(
        df_display[["session_date", "subject_id", "duration", "notes"]],
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
    total_min = df["duration"].sum()
    session_count = len(df)
    last_session = df["session_date"].max().strftime("%d.%m.%Y %H:%M")

    cols = st.columns(3)
    cols[0].metric("Total time", f"{int(total_min)} min")
    cols[1].metric("Sessions", session_count)
    cols[2].metric("Last session", last_session)

    # Charts
    st.subheader("Progress Charts")

    # Bar chart
    time_by_subject = df.groupby("subject_id")["duration"].sum().reset_index()
    time_by_subject["subject_id"] = "Subject " + time_by_subject["subject_id"].astype(str)

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.bar(time_by_subject["subject_id"], time_by_subject["duration"], color="#4CAF50")
    ax1.set_title("Total Study Time per Subject")
    ax1.set_xlabel("Subject")
    ax1.set_ylabel("Minutes")
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

    # Line chart
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
    st.info("No study sessions yet. Add your first one above.")