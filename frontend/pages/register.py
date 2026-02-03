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
                f"{API_BASE}/register",
                json={"username": username, "email": email, "password": password}
            )
            if r.status_code == 200:
                data = r.json()
                st.success(f"Account created! Your ID: {data['user_id']}")
                st.info("You can now go back and log in.")
                st.markdown("[Go to login →](pages/login.py)")
            else:
                st.error(r.json().get("detail", "Registration failed"))
        except Exception as e:
            st.error(f"Could not connect to server: {e}")