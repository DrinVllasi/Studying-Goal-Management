# main.py
from fastapi import FastAPI, HTTPException, Header, Response, status
from database import get_db, init_db
from schemas import (
    UserCreate,
    UserOut,
    StudySessionCreate,
    StudySessionOut,
    Login,
    Subject,
    SubjectCreate,      
    HabitCreate, HabitOut,  
    GoalCreate, GoalOut     
)
from typing import List
import sqlite3

app = FastAPI(title="Study Goal API")

@app.on_event("startup")
async def startup_event():
    init_db()

# ────────────────────────────────────────────────
# Subjects CRUD
# ────────────────────────────────────────────────

@app.get("/subjects/", response_model=List[Subject])
def get_subjects():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM subjects ORDER BY name")
    rows = cursor.fetchall()
    db.close()
    return [{"id": row["id"], "name": row["name"]} for row in rows]


@app.post("/subjects/", response_model=Subject, status_code=201)
def create_subject(subject: SubjectCreate):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO subjects (name) VALUES (?)", (subject.name,))
        db.commit()
        subject_id = cursor.lastrowid
        cursor.execute("SELECT id, name FROM subjects WHERE id = ?", (subject_id,))
        row = cursor.fetchone()
        return {"id": row["id"], "name": row["name"]}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Subject name already exists")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()


@app.put("/subjects/{subject_id}", response_model=Subject)
def update_subject(subject_id: int, subject: SubjectCreate):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE subjects SET name = ? WHERE id = ?", (subject.name, subject_id))
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Subject not found")
        cursor.execute("SELECT id, name FROM subjects WHERE id = ?", (subject_id,))
        row = cursor.fetchone()
        return {"id": row["id"], "name": row["name"]}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Subject name already exists")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()


@app.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(subject_id: int):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Subject not found")
        return Response(status_code=204)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

# ────────────────────────────────────────────────
# Your existing endpoints (kept unchanged)
# ────────────────────────────────────────────────

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

        cursor.execute(
            "SELECT id, username, email FROM users WHERE id = ?",
            (user_id,)
        )
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
    cursor.execute(
        "SELECT id, username, email FROM users WHERE id = ?",
        (x_user_id,)
    )
    row = cursor.fetchone()
    db.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": row[0], "username": row[1], "email": row[2]}


@app.post("/study/", status_code=201)
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
            INSERT INTO study_sessions
            (user_id, subject_id, duration, notes, session_date)
            VALUES (?, ?, ?, ?, datetime('now'))
            """,
            (session.user_id, session.subject_id, session.duration, session.notes)
        )
        db.commit()
        return Response(status_code=201)
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

    sessions: List[StudySessionOut] = []

    for row in rows:
        sessions.append(
            StudySessionOut(
                id=row[0],
                user_id=row[1],
                subject_id=row[2],
                duration=row[3],
                notes=row[4],
                session_date=row[5]
            )
        )

    return sessions
# Update a session (PUT /study/{session_id})
@app.put("/study/{session_id}", status_code=200)
def update_study_session(
    session_id: int,
    updates: StudySessionCreate,
    x_user_id: int = Header(..., alias="X-User-Id")
):
    db = get_db()
    cursor = db.cursor()

    # Check if the session exists and belongs to the user
    cursor.execute(
        "SELECT user_id FROM study_sessions WHERE id = ?",
        (session_id,)
    )
    row = cursor.fetchone()
    if not row:
        db.close()
        raise HTTPException(status_code=404, detail="Session not found")

    if row["user_id"] != x_user_id:
        db.close()
        raise HTTPException(status_code=403, detail="You can only edit your own sessions")

    # Build the update query dynamically (only update fields that are provided)
    fields = []
    values = []
    if updates.subject_id is not None:
        fields.append("subject_id = ?")
        values.append(updates.subject_id)
    if updates.duration is not None:
        fields.append("duration = ?")
        values.append(updates.duration)
    if updates.notes is not None:
        fields.append("notes = ?")
        values.append(updates.notes)

    if not fields:
        db.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(session_id)
    query = f"UPDATE study_sessions SET {', '.join(fields)} WHERE id = ?"

    try:
        cursor.execute(query, values)
        db.commit()
        return {"message": "Session updated successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()


# Delete a session (DELETE /study/{session_id})
@app.delete("/study/{session_id}", status_code=204)
def delete_study_session(
    session_id: int,
    x_user_id: int = Header(..., alias="X-User-Id")
):
    db = get_db()
    cursor = db.cursor()

    # Check ownership
    cursor.execute(
        "SELECT user_id FROM study_sessions WHERE id = ?",
        (session_id,)
    )
    row = cursor.fetchone()
    if not row:
        db.close()
        raise HTTPException(status_code=404, detail="Session not found")

    if row["user_id"] != x_user_id:
        db.close()
        raise HTTPException(status_code=403, detail="You can only delete your own sessions")

    try:
        cursor.execute("DELETE FROM study_sessions WHERE id = ?", (session_id,))
        db.commit()
        return Response(status_code=204)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

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