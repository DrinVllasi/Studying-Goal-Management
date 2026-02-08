import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_BASE = "http://127.0.0.1:8000"

# ────────────────────────────────────────────────
# Auto-login for development (remove later)
# ────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state["user_id"] = 1
    st.info("Development mode: auto-logged in as user ID 1")

if "user_id" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

user_id = st.session_state["user_id"]

# ────────────────────────────────────────────────
# Fetch subjects for dropdown and name mapping
# ────────────────────────────────────────────────
subjects = []
try:
    r = requests.get(f"{API_BASE}/subjects/")
    if r.status_code == 200:
        subjects = r.json()
    else:
        st.warning("Could not load subjects")
except Exception as e:
    st.warning(f"Error loading subjects: {e}")

# Subject name mapping (id → name)
subject_map = {s["id"]: s["name"] for s in subjects} if subjects else {}

# ────────────────────────────────────────────────
# Sidebar with logout
# ────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**Logged in** as User ID: {user_id}")

    if st.button("Log out", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")
        st.rerun()

st.title("Study Dashboard")
st.caption(f"User ID: {user_id}")

# ────────────────────────────────────────────────
# Add new study session form
# ────────────────────────────────────────────────
st.subheader("Log new study session")

with st.form("new_session_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        if subjects:
            subject_names = [s["name"] for s in subjects]
            selected_name = st.selectbox(
                "Subject",
                options=subject_names,
                index=0,
                help="Choose what you're studying"
            )
            # Get ID from name
            subject_id = next(s["id"] for s in subjects if s["name"] == selected_name)
        else:
            subject_id = st.number_input("Subject ID (fallback)", min_value=1, value=1)

    with col2:
        duration = st.number_input(
            "Duration (minutes)",
            min_value=5,
            step=5,
            value=30
        )

    notes = st.text_area(
        "Notes",
        height=100,
        placeholder="What did you study / how did it go?"
    )

    submitted = st.form_submit_button("Save session", use_container_width=True)

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

                if r.status_code in (200, 201):
                    st.success("Session saved!")
                    st.rerun()
                else:
                    st.error(f"Server error ({r.status_code}): {r.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the API: {e}")

# ────────────────────────────────────────────────
# Fetch study sessions
# ────────────────────────────────────────────────
sessions = []

try:
    r = requests.get(
        f"{API_BASE}/study",
        headers={"X-User-Id": str(user_id)}
    )

    if r.status_code == 200:
        sessions = r.json()
    else:
        st.error(f"Could not load sessions ({r.status_code})")

except Exception as e:
    st.error(f"Connection error: {e}")

# ────────────────────────────────────────────────
# Display data
# ────────────────────────────────────────────────
if sessions:
    df = pd.DataFrame(sessions)
    df["session_date"] = pd.to_datetime(df["session_date"])
    df = df.sort_values("session_date", ascending=False)

    # Add subject name column
    df["subject_name"] = df["subject_id"].map(subject_map).fillna(df["subject_id"].astype(str))

    df_display = df.copy()
    df_display["duration"] = df_display["duration"].astype(str) + " min"
    df_display["notes"] = df_display["notes"].fillna("-")

    st.dataframe(
        df_display[["session_date", "subject_name", "duration", "notes"]],
        hide_index=True,
        use_container_width=True
    )

    # Stats
    total_min = int(df["duration"].sum())
    session_count = len(df)
    last_session = df["session_date"].max().strftime("%d.%m.%Y %H:%M")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total time", f"{total_min} min")
    c2.metric("Sessions", session_count)
    c3.metric("Last session", last_session)

    # Charts
    st.subheader("Progress Charts")

    time_by_subject = df.groupby("subject_name")["duration"].sum()  # use name now

    fig1, ax1 = plt.subplots()
    ax1.bar(time_by_subject.index, time_by_subject.values)
    ax1.set_title("Total Study Time per Subject")
    ax1.set_xlabel("Subject")
    ax1.set_ylabel("Minutes")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig1)

    daily = df.groupby(df["session_date"].dt.date)["duration"].sum()

    fig2, ax2 = plt.subplots()
    ax2.plot(daily.index, daily.values, marker="o")
    ax2.set_title("Daily Study Time")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Minutes")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

else:
    st.info("No study sessions yet. Add your first one above.")