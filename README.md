# Studying Goal Management

A simple full-stack app to track study sessions, set goals (milestone and daily), and see your progress.

- FastAPI backend (API + SQLite database)
- Streamlit frontend (dashboard + goals page)

## Features
- Register / log in
- Log study sessions (subject, duration, notes)
- See sessions table, stats, charts (time per subject, daily trend)
- Set milestone goals (progress %, target date)
- Set daily goals (streak + mark done today)
- Edit / delete sessions and goals
- Subjects dropdown with real names

## Requirements
- Python 3.10 or higher

## How to Install & Run

### 1. Clone the project
```bash
git clone https://github.com/DrinVllasi/Studying-Goal-Management.git
cd Studying-Goal-Management

### 2. Install libraries
pip install -r requirements.txt

### 3. Start the backend
#Open terminal1 and run:
cd backend   # if your main.py is inside a 'backend' folder
uvicorn main:app --reload

### 4. Start the frontend
#Open terminal2 and run:
cd frontend # if your app.py is inside a 'frontend' folder
streamlit run app.py