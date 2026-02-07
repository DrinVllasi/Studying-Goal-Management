# main.py
from fastapi import FastAPI, HTTPException, Header
from database import get_db, init_db
from schemas import UserCreate, UserOut, StudySessionCreate, StudySessionOut, Login
from typing import List

app = FastAPI(title="Study Goal API")


@app.on_event("startup")
def startup_event():
    init_db()


# ──────────────── Users ────────────────

@app.post("/users/", response_model=UserOut, status_code=201)
def create_user(user: UserCreate):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users (username, email, password, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (user.username, user.email, user.password)
        )
        db.commit()
        user_id = cursor.lastrowid

        # Return the created user
        cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return {"id": row[0], "username": row[1], "email": row[2]}

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already taken")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()


@app.get("/users/me", response_model=UserOut)
def get_current_user(x_user_id: int = Header(..., alias="X-User-Id")):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (x_user_id,))
    row = cursor.fetchone()
    db.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return UserOut(id=row[0], username=row[1], email=row[2])


# ──────────────── Study Sessions ────────────────

@app.post("/study/", response_model=StudySessionOut, status_code=201)
def create_study_session(
        session: StudySessionCreate,
        x_user_id: int = Header(..., alias="X-User-Id")
):
    if session.user_id != x_user_id:
        raise HTTPException(status_code=403, detail="You can only create sessions for yourself")

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO study_sessions (user_id, subject_id, duration, notes, session_date)
            VALUES (?, ?, ?, ?, datetime('now'))
            """,
            (session.user_id, session.subject_id, session.duration, session.notes)
        )
        db.commit()
        session_id = cursor.lastrowid

        # Return the created session
        cursor.execute(
            "SELECT id, user_id, subject_id, duration, notes, session_date FROM study_sessions WHERE id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        return StudySessionOut(
            id=row[0], user_id=row[1], subject_id=row[2],
            duration=row[3], notes=row[4], session_date=row[5]
        )

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()


@app.get("/study/", response_model=List[StudySessionOut])
def get_my_study_sessions(x_user_id: int = Header(..., alias="X-User-Id")):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id, user_id, subject_id, duration, notes, session_date
        FROM study_sessions
        WHERE user_id = ?
        ORDER BY session_date DESC
        """,
        (x_user_id,)
    )
    rows = cursor.fetchall()
    db.close()

    sessions = []
    for row in rows:
        sessions.append(StudySessionOut(
            id=row[0], user_id=row[1], subject_id=row[2],
            duration=row[3], notes=row[4], session_date=row[5]
        ))

    return sessions


@app.post("/login")
def login(credentials: Login):
    user = get_user_by_username(credentials.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {"message": "Login successful", "user_id": user["id"]}

def get_user_by_username(username: str):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, username, password FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    db.close()
    if row:
        return {"id": row[0], "username": row[1], "password": row[2]}
    return None