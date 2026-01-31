from fastapi import FastAPI
from fastapi import HTTPException
from database import init_db
from schemas import UserCreate
from schemas import StudySessionCreate
from crud import create_user
from crud import add_study_session


app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Study & Growth API running"}

@app.post("/register")
def register(user: UserCreate):
    user_id = create_user(user.username, user.email, user.password)
    if user_id is None:
        raise HTTPException(status_code=400, detail="Username or email already taken")
    return {"message": "User registered", "user_id": user_id}

@app.post("/study")
def create_study(session: StudySessionCreate):
    add_study_session(
        session.user_id,
        session.subject,
        session.duration,
        session.notes
    )
    return {"message": "Study session added"}