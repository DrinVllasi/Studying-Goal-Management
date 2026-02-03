# crud.py
import sqlite3


def get_db():
    return sqlite3.connect("study.db", check_same_thread=False)


def create_user(username: str, email: str, password: str) -> int | None:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users (username, email, password, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (username, email, password)
        )
        db.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    except sqlite3.Error as e:
        print(f"Database error in create_user: {e}")
        return None
    finally:
        db.close()


def add_study_session(user_id: int, subject_id: int, duration: int, notes: str = None) -> int | None:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO study_sessions (user_id, subject_id, duration, notes, session_date) VALUES (?, ?, ?, ?, datetime('now'))",
            (user_id, subject_id, duration, notes)
        )
        db.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"DB error in add_study_session: {e}")
        return None
    finally:
        db.close()

def get_user_by_username(username: str) -> dict | None:
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, username, password FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    db.close()
    if row:
        return {
            "id": row[0],
            "username": row[1],
            "password": row[2]
        }
    return None

def get_user_by_id(user_id: int) -> dict | None:
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, username FROM users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    db.close()
    if row:
        return {
            "id": row[0],
            "username": row[1]
        }
    return None

def get_study_sessions_for_user(user_id: int) -> list[dict]:
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT 
            id,
            subject_id,
            duration,
            notes,
            session_date
        FROM study_sessions
        WHERE user_id = ?
        ORDER BY session_date DESC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    db.close()

    # Convert rows to list of dicts
    sessions = []
    for row in rows:
        sessions.append({
            "id": row[0],
            "subject_id": row[1],
            "duration": row[2],
            "notes": row[3],
            "session_date": row[4]
        })

    return sessions