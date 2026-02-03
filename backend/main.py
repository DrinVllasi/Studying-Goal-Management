from fastapi import FastAPI, HTTPException, Header
from database import init_db
from schemas import UserCreate
from schemas import StudySessionCreate, Login
from crud import create_user, get_user_by_username, get_user_by_id, get_study_sessions_for_user
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
        raise HTTPException(
            status_code=400,
            detail="Username or email is already taken"
        )
    return {
        "message": "User registered successfully",
        "user_id": user_id
    }

@app.post("/login")
def login(credentials: Login):
    user = get_user_by_username(credentials.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {"message": "Login successful", "user_id": user["id"]}

@app.post("/study")
def create_study(
    session: StudySessionCreate,
    x_user_id: int = Header(None, alias="X-User-Id")
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header - please login first")

    user = get_user_by_id(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    if session.user_id != x_user_id:
        raise HTTPException(status_code=403, detail="You can only create sessions for yourself")

    new_id = add_study_session(
        user_id=session.user_id,
        subject_id=session.subject,
        duration=session.duration,
        notes=session.notes
    )

    if new_id is None:
        raise HTTPException(status_code=500, detail="Failed to create study session")

    return {"message": "Study session added", "session_id": new_id}

@app.get("/study")
def get_study_sessions(x_user_id: int = Header(None, alias="X-User-Id")):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")

    user = get_user_by_id(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    sessions = get_study_sessions_for_user(x_user_id)   

    if not sessions:
        return {"message": "No study sessions found", "sessions": []}

    return {"sessions": sessions}

