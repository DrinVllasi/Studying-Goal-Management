import streamlit as st
import requests


API_BASE = "http://127.0.0.1:8000"

st.title("Create Account")

with st.form("register_form"):
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Register", type="primary")

if submit:
    if not all([username, email, password]):
        st.error("All fields are required")
    else:
        try:
            r = requests.post(
                f"{API_BASE}/users/",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                }
            )

            if r.status_code == 201:  # 201 Created
                data = r.json()
                st.success(f"Account created! Your ID: {data['id']}")
                st.info("You can now log in.")
                st.markdown("[Go back to login →](app.py)")  # or use st.switch_page
            else:
                try:
                    detail = r.json().get("detail", "Registration failed")
                    st.error(detail)
                except:
                    st.error(f"Server error ({r.status_code})")

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the API. Is the backend running?")
        except Exception as e:
            st.error(f"An error occurred: {e}")