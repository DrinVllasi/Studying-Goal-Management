import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.title("Welcome to Study & Goal Manager!")
st.markdown("Log in or create an account.")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Log In", type="primary")

if submit:
    if not username or not password:
        st.error("Please enter both username and password")
    else:
        try:
            r = requests.post(
                f"{API_BASE}/login",
                json={"username": username, "password": password}
            )

            if r.status_code == 200:
                data = r.json()
                st.session_state["user_id"] = data["user_id"]
                st.success("Logged in successfully!")
                st.switch_page("pages/dashboard.py")
            else:
                try:
                    detail = r.json().get("detail", "Login failed")
                    st.error(detail)
                except:
                    st.error(f"Server error ({r.status_code})")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the API. Is the backend running?")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if st.button("No account yet? Register here", type="secondary"):
    st.switch_page("pages/register.py")