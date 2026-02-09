# crud.py
import sqlite3
from typing import List, Dict, Optional

def get_db():
    conn = sqlite3.connect("study.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row  # makes rows dict-like
    return conn


# ────────────────────────────────────────────────
# Users CRUD
# ────────────────────────────────────────────────
def create_user(username: str, email: str, password: str) -> Optional[int]:
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
        return None  # duplicate username/email
    except sqlite3.Error as e:
        print(f"DB error creating user: {e}")
        return None
    finally:
        db.close()


def get_user_by_id(user_id: int) -> Optional[Dict]:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    db.close()
    return dict(row) if row else None


def get_user_by_username(username: str) -> Optional[Dict]:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    db.close()
    return dict(row) if row else None


def update_user(user_id: int, username: Optional[str] = None, email: Optional[str] = None, password: Optional[str] = None) -> bool:
    db = get_db()
    cursor = db.cursor()
    updates = []
    params = []
    if username:
        updates.append("username = ?")
        params.append(username)
    if email:
        updates.append("email = ?")
        params.append(email)
    if password:
        updates.append("password = ?")
        params.append(password)
    if not updates:
        return False
    params.append(user_id)
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
    try:
        cursor.execute(query, params)
        db.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"DB error updating user: {e}")
        return False
    finally:
        db.close()


def delete_user(user_id: int) -> bool:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"DB error deleting user: {e}")
        return False
    finally:
        db.close()


# ────────────────────────────────────────────────
# Study Sessions CRUD
# ────────────────────────────────────────────────
def create_study_session(user_id: int, subject_id: int, duration: int, notes: Optional[str] = None) -> Optional[int]:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO study_sessions (user_id, subject_id, duration, notes, session_date)
            VALUES (?, ?, ?, ?, datetime('now'))
            """,
            (user_id, subject_id, duration, notes)
        )
        db.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"DB error creating session: {e}")
        return None
    finally:
        db.close()


def get_study_session(session_id: int) -> Optional[Dict]:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM study_sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    db.close()
    return dict(row) if row else None


def get_study_sessions_for_user(user_id: int) -> List[Dict]:
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id, user_id, subject_id, duration, notes, session_date
        FROM study_sessions
        WHERE user_id = ?
        ORDER BY session_date DESC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    db.close()
    return [dict(row) for row in rows]


def update_study_session(session_id: int, subject_id: Optional[int] = None, duration: Optional[int] = None, notes: Optional[str] = None) -> bool:
    db = get_db()
    cursor = db.cursor()
    updates = []
    params = []
    if subject_id is not None:
        updates.append("subject_id = ?")
        params.append(subject_id)
    if duration is not None:
        updates.append("duration = ?")
        params.append(duration)
    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)
    if not updates:
        return False
    params.append(session_id)
    query = f"UPDATE study_sessions SET {', '.join(updates)} WHERE id = ?"
    try:
        cursor.execute(query, params)
        db.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"DB error updating session: {e}")
        return False
    finally:
        db.close()


def delete_study_session(session_id: int) -> bool:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM study_sessions WHERE id = ?", (session_id,))
        db.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"DB error deleting session: {e}")
        return False
    finally:
        db.close()


# ────────────────────────────────────────────────
# Subjects CRUD (simple, add as needed)
# ────────────────────────────────────────────────
def create_subject(name: str) -> Optional[int]:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
        db.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # duplicate name
    finally:
        db.close()


def get_all_subjects() -> List[Dict]:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM subjects ORDER BY name")
    rows = cursor.fetchall()
    db.close()
    return [dict(row) for row in rows]


def update_subject(subject_id: int, name: str) -> bool:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE subjects SET name = ? WHERE id = ?", (name, subject_id))
        db.commit()
        return cursor.rowcount > 0
    finally:
        db.close()


def delete_subject(subject_id: int) -> bool:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        db.commit()
        return cursor.rowcount > 0
    finally:
        db.close()


# ────────────────────────────────────────────────
# Habits & Goals CRUD (placeholder, implement as needed)
# ────────────────────────────────────────────────