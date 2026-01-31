# crud.py
import sqlite3


def get_db():
    return sqlite3.connect("study.db", check_same_thread=False)


def create_user(username: str, email: str, password: str) -> int | None:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, datetime('now'))",
            (username, email, password)
        )
        db.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # username or email already taken
    except sqlite3.Error as e:
        print(f"DB error in create_user: {e}")
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