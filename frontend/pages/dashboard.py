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
# Fetch subjects for name mapping
# ────────────────────────────────────────────────
subject_map = {}
try:
    r = requests.get(f"{API_BASE}/subjects/")
    if r.status_code == 200:
        subjects = r.json()
        subject_map = {s["id"]: s["name"] for s in subjects}
    else:
        st.warning("Could not load subject names")
except Exception as e:
    st.warning(f"Error loading subjects: {e}")

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
st.subheader("Add New Session")

with st.form("new_session_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        if subject_map:
            subject_names = list(subject_map.values())
            selected_name = st.selectbox("Subject", options=subject_names, index=0)
            subject_id = next((k for k, v in subject_map.items() if v == selected_name), 1)
        else:
            subject_id = st.number_input("Subject ID (fallback)", min_value=1, value=1)

    with col2:
        duration = st.number_input("Duration (minutes)", min_value=5, step=5, value=30)

    notes = st.text_area("Notes", height=100, placeholder="What did you study / how did it go?")

    if st.form_submit_button("Save", type="primary", use_container_width=True):
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
            except Exception as e:
                st.error(f"Could not reach the API: {e}")

# ────────────────────────────────────────────────
# Fetch sessions
# ────────────────────────────────────────────────
sessions = []
try:
    r = requests.get(f"{API_BASE}/study", headers={"X-User-Id": str(user_id)})
    if r.status_code == 200:
        sessions = r.json() if isinstance(r.json(), list) else r.json().get("sessions", [])
    else:
        st.error(f"Could not load sessions ({r.status_code})")
except Exception as e:
    st.error(f"Connection error: {e}")

# ────────────────────────────────────────────────
# Display sessions
# ────────────────────────────────────────────────
if sessions:
    df = pd.DataFrame(sessions)
    df["session_date"] = pd.to_datetime(df["session_date"])
    df = df.sort_values("session_date", ascending=False)
    df["subject_name"] = df["subject_id"].map(subject_map).fillna(df["subject_id"].astype(str))

    df_display = df.copy()
    df_display["duration"] = df_display["duration"].astype(int).astype(str) + " min"
    df_display["notes"] = df_display["notes"].fillna("-")

    st.dataframe(
        df_display[["session_date", "subject_name", "duration", "notes"]],
        hide_index=True,
        column_config={
            "session_date": st.column_config.DateColumn("Date", format="DD.MM.YYYY HH:mm"),
            "subject_name": st.column_config.TextColumn("Subject"),
            "duration": st.column_config.TextColumn("Duration"),
            "notes": st.column_config.TextColumn("Notes")
        },
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

    # ────────────────────────────────────────────────-
    # Modern black-and-white Charts with darker background
    # ────────────────────────────────────────────────-
    st.subheader("Progress Charts")

    # Bar chart - dark gray bars, off-white background
    time_by_subject = df.groupby("subject_name")["duration"].sum().reset_index()

    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.bar(time_by_subject["subject_name"], time_by_subject["duration"], color="#202020", width=0.5)
    ax1.set_title("Total Study Time per Subject", fontsize=25, pad=25)
    ax1.set_xlabel("Subject", fontsize=15, labelpad=12)
    ax1.set_ylabel("Minutes", fontsize=15, labelpad=12)
    ax1.tick_params(axis='both', which='major', labelsize=11)

    # Darker background
    ax1.set_facecolor("#B3B1B1")
    fig1.set_facecolor("#B3B1B1")

    # Clean spines
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color("#000000")
    ax1.spines['bottom'].set_color("#000000")

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig1)

    # Line chart - dark line, light fill, off-white background
    daily = df.groupby(df["session_date"].dt.date)["duration"].sum().reset_index()
    daily["session_date"] = pd.to_datetime(daily["session_date"])

    fig2, ax2 = plt.subplots(figsize=(14, 6))
    ax2.plot(daily["session_date"], daily["duration"], color="#020A1B", linewidth=3)
    ax2.fill_between(daily["session_date"], daily["duration"], color="#000000", alpha=0.5)

    ax2.set_title("Daily Study Time", fontsize=25, pad=25)
    ax2.set_xlabel("Date", fontsize=1, labelpad=12)
    ax2.set_ylabel("Minutes", fontsize=15, labelpad=12)
    ax2.tick_params(axis='both', which='major', labelsize=11)

    # Darker background
    ax2.set_facecolor('#f8f9fa')
    fig2.set_facecolor('#f8f9fa')

    # Clean spines
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color("#000000")
    ax2.spines['bottom'].set_color("#000000")

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig2)

else:
    st.info("No study sessions yet. Add your first one above.")

# ────────────────────────────────────────────────
# Manage Sessions (edit/delete - unchanged)
# ────────────────────────────────────────────────
if sessions:
    st.subheader("Manage Sessions")

    for _, row in df.iterrows():
        session_id = row["id"]
        label = f"{row['session_date'].strftime('%d.%m.%Y %H:%M')} • {row['duration']} min • {row['subject_name']}"
        with st.expander(label):
            col_left, col_right = st.columns([3, 1])

            with col_left:
                new_duration = st.number_input(
                    "New Duration (minutes)",
                    min_value=1,
                    value=int(row["duration"]),
                    key=f"dur_{session_id}"
                )
                new_notes = st.text_area(
                    "New Notes",
                    value=row["notes"] or "",
                    height=80,
                    key=f"notes_{session_id}"
                )

            with col_right:
                confirm = st.checkbox("Confirm delete", key=f"confirm_{session_id}")
                if st.button("Delete", type="primary", disabled=not confirm, key=f"delete_{session_id}"):
                    try:
                        r = requests.delete(
                            f"{API_BASE}/study/{session_id}",
                            headers={"X-User-Id": str(user_id)}
                        )
                        if r.status_code in (200, 204):
                            st.success("Session deleted!")
                            st.rerun()
                        else:
                            st.error(r.text)
                    except Exception as e:
                        st.error(f"Error deleting: {e}")

                if st.button("Update", key=f"update_{session_id}", use_container_width=True):
                    try:
                        r = requests.put(
                            f"{API_BASE}/study/{session_id}",
                            json={
                                "user_id": user_id,
                                "subject_id": row["subject_id"],
                                "duration": new_duration,
                                "notes": new_notes.strip() or None
                            },
                            headers={"X-User-Id": str(user_id)}
                        )
                        if r.status_code in (200, 204):
                            st.success("Session updated!")
                            st.rerun()
                        else:
                            st.error(r.text)
                    except Exception as e:
                        st.error(f"Error updating: {e}")