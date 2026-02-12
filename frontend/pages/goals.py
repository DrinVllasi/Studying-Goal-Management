import streamlit as st
import requests
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"

# Auto-login fallback (remove later)
if "user_id" not in st.session_state:
    st.session_state["user_id"] = 1
    st.info("Dev mode: auto-logged in as user ID 1")

if "user_id" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

user_id = st.session_state["user_id"]

# Sidebar
with st.sidebar:
    st.markdown(f"**Logged in** as User ID: {user_id}")
    if st.button("Log out", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")
        st.rerun()

st.title("My Goals")

# Fetch goals
goals = []
try:
    r = requests.get(f"{API_BASE}/goals/", headers={"X-User-Id": str(user_id)})
    if r.status_code == 200:
        goals = r.json()
    else:
        st.error(f"Could not load goals ({r.status_code})")
except Exception as e:
    st.error(f"Connection error: {e}")

# ────────────────────────────────────────────────
# Add Milestone Goal
# ────────────────────────────────────────────────
with st.expander("Add Milestone Goal", expanded=False):
    with st.form("add_milestone_form"):
        title = st.text_input("Goal Title", placeholder="e.g. Finish Python course")
        category = st.selectbox("Category", options=["Study", "Health", "Productivity", "Other"], index=0)
        progress = st.slider("Current Progress (%)", 0, 100, 0)
        target_date = st.date_input("Target Date (optional)", value=None)

        submitted = st.form_submit_button("Create Milestone Goal", type="primary")

        if submitted and title.strip():
            try:
                payload = {
                    "user_id": user_id,
                    "title": title.strip(),
                    "category": category,
                    "progress": progress,
                    "target_date": str(target_date) if target_date else None,
                    "type": "milestone"
                }
                r = requests.post(f"{API_BASE}/goals/", json=payload, headers={"X-User-Id": str(user_id)})
                if r.status_code in (200, 201):
                    st.success("Milestone goal created!")
                    st.rerun()
                else:
                    st.error(r.text)
            except Exception as e:
                st.error(f"Error: {e}")

# ────────────────────────────────────────────────
# Add Daily Goal
# ────────────────────────────────────────────────
with st.expander("Add Daily Goal", expanded=False):
    with st.form("add_daily_form"):
        title = st.text_input("Daily Goal Title", placeholder="e.g. Drink 2L of water")
        category = st.selectbox("Category", options=["Study", "Health", "Productivity", "Other"], index=0)

        submitted = st.form_submit_button("Create Daily Goal", type="primary")

        if submitted and title.strip():
            try:
                payload = {
                    "user_id": user_id,
                    "title": title.strip(),
                    "category": category,
                    "progress": 0,
                    "target_date": None,
                    "type": "daily"
                }
                r = requests.post(f"{API_BASE}/goals/", json=payload, headers={"X-User-Id": str(user_id)})
                if r.status_code in (200, 201):
                    st.success("Daily goal created!")
                    st.rerun()
                else:
                    st.error(r.text)
            except Exception as e:
                st.error(f"Error: {e}")

# ────────────────────────────────────────────────
# Display Goals
# ────────────────────────────────────────────────
if goals:
    st.subheader("Your Goals")

    milestone_goals = [g for g in goals if g.get("type") == "milestone"]
    daily_goals = [g for g in goals if g.get("type") == "daily"]

    today = datetime.now().date().isoformat()

    # Milestone Goals
    if milestone_goals:
        st.markdown("### Milestone Goals")
        for goal in milestone_goals:
            progress = goal.get("progress", 0)
            title = goal.get("title", "Unnamed goal")
            category = goal.get("category", "—")
            target = goal.get("target_date") or "No deadline"

            # Color gradient
            if progress <= 30:
                color = "#FF4D4D"  # red
            elif progress <= 60:
                color = "#FFA500"  # orange
            elif progress <= 90:
                color = "#FFEB3B"  # yellow
            else:
                color = "#4CAF50"  # green

            st.markdown(f"**{title}** ({category}) — Target: {target}")
            st.progress(progress / 100, text=f"{progress}%")

            # Custom color override
            st.markdown(
                f"""
                <style>
                    .stProgress > div > div > div > div {{
                        background-color: {color} !important;
                    }}
                </style>
                """,
                unsafe_allow_html=True
            )

            # Edit & Delete
            col1, col2 = st.columns(2)
            with col1:
                edit_key = f"edit_expanded_{goal['id']}"
                if st.button("Edit", key=f"edit_btn_{goal['id']}"):
                    st.session_state[edit_key] = True
                    st.rerun()

                if st.session_state.get(edit_key, False):
                    with st.expander(f"Edit '{title}'", expanded=True):
                        new_title = st.text_input("Title", value=title, key=f"title_{goal['id']}")
                        new_category = st.selectbox(
                            "Category",
                            ["Study", "Health", "Productivity", "Other"],
                            index=["Study", "Health", "Productivity", "Other"].index(category) if category in ["Study", "Health", "Productivity", "Other"] else 0,
                            key=f"cat_{goal['id']}"
                        )
                        new_progress = st.slider("Progress (%)", 0, 100, progress, key=f"prog_{goal['id']}")
                        new_target = st.date_input(
                            "Target Date",
                            value=datetime.strptime(goal['target_date'], "%Y-%m-%d") if goal['target_date'] and goal['target_date'] != "No deadline" else None,
                            key=f"targ_{goal['id']}"
                        )

                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("Save Changes", type="primary", key=f"save_{goal['id']}"):
                                try:
                                    payload = {
                                        "user_id": user_id,
                                        "title": new_title,
                                        "category": new_category,
                                        "progress": new_progress,
                                        "target_date": str(new_target) if new_target else None
                                    }
                                    r = requests.put(f"{API_BASE}/goals/{goal['id']}", json=payload, headers={"X-User-Id": str(user_id)})
                                    if r.status_code in (200, 204):
                                        st.success("Goal updated!")
                                        st.session_state[edit_key] = False
                                        st.rerun()
                                    else:
                                        st.error(r.text)
                                except Exception as e:
                                    st.error(f"Error: {e}")

                        with col_cancel:
                            if st.button("Cancel", key=f"cancel_{goal['id']}"):
                                st.session_state[edit_key] = False
                                st.rerun()

            with col2:
                confirm_key = f"confirm_del_{goal['id']}"
                confirm = st.checkbox("Confirm delete", key=confirm_key)
                if st.button("Delete", type="primary", disabled=not confirm, key=f"del_{goal['id']}"):
                    try:
                        r = requests.delete(f"{API_BASE}/goals/{goal['id']}", headers={"X-User-Id": str(user_id)})
                        if r.status_code in (200, 204):
                            st.success("Goal deleted!")
                            st.rerun()
                        else:
                            st.error(r.text)
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Daily Goals
    if daily_goals:
        st.markdown("### Daily Goals")

        for goal in daily_goals:
            title = goal.get("title", "Unnamed daily goal")
            category = goal.get("category", "—")
            streak = goal.get("streak", 0)
            last_done = goal.get("last_done")

            done_today = last_done == datetime.now().date().isoformat()

            st.markdown(f"**{title}** ({category}) — Streak: **{streak}** 🔥")

            if done_today:
                st.success("Done today ✓")
            else:
                if st.button("Mark Done Today", type="primary", key=f"mark_{goal['id']}"):
                    try:
                        r = requests.post(f"{API_BASE}/goals/{goal['id']}/mark-daily", headers={"X-User-Id": str(user_id)})
                        if r.status_code == 200:
                            st.success("Marked done!")
                            st.rerun()
                        else:
                            st.error(r.text)
                    except Exception as e:
                        st.error(f"Error: {e}")

            # Edit & Delete for daily goals
            col1, col2 = st.columns(2)
            with col1:
                edit_key = f"edit_expanded_{goal['id']}"
                if st.button("Edit", key=f"edit_btn_{goal['id']}"):
                    st.session_state[edit_key] = True
                    st.rerun()

                if st.session_state.get(edit_key, False):
                    with st.expander(f"Edit '{title}'", expanded=True):
                        new_title = st.text_input("Title", value=title, key=f"title_{goal['id']}")
                        new_category = st.selectbox(
                            "Category",
                            ["Study", "Health", "Productivity", "Other"],
                            index=["Study", "Health", "Productivity", "Other"].index(category) if category in ["Study", "Health", "Productivity", "Other"] else 0,
                            key=f"cat_{goal['id']}"
                        )

                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("Save Changes", type="primary", key=f"save_{goal['id']}"):
                                try:
                                    payload = {
                                        "user_id": user_id,
                                        "title": new_title,
                                        "category": new_category,
                                        "progress": 0,
                                        "target_date": None
                                    }
                                    r = requests.put(f"{API_BASE}/goals/{goal['id']}", json=payload, headers={"X-User-Id": str(user_id)})
                                    if r.status_code in (200, 204):
                                        st.success("Goal updated!")
                                        st.session_state[edit_key] = False
                                        st.rerun()
                                    else:
                                        st.error(r.text)
                                except Exception as e:
                                    st.error(f"Error: {e}")

                        with col_cancel:
                            if st.button("Cancel", key=f"cancel_{goal['id']}"):
                                st.session_state[edit_key] = False
                                st.rerun()

            with col2:
                confirm_key = f"confirm_del_{goal['id']}"
                confirm = st.checkbox("Confirm delete", key=confirm_key)
                if st.button("Delete", type="primary", disabled=not confirm, key=f"del_{goal['id']}"):
                    try:
                        r = requests.delete(f"{API_BASE}/goals/{goal['id']}", headers={"X-User-Id": str(user_id)})
                        if r.status_code in (200, 204):
                            st.success("Goal deleted!")
                            st.rerun()
                        else:
                            st.error(r.text)
                    except Exception as e:
                        st.error(f"Error: {e}")

else:
    st.info("No goals yet. Add your first one above!")