import sqlite3


def get_db():
    """
    Returns a connection to the database with row_factory set to sqlite3.Row
    (so fetchone/fetchall return dict-like objects).
    """
    conn = sqlite3.connect("study.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Creates all required tables if they don't exist.
    Should be called once on startup.
    """
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT UNIQUE NOT NULL,
                email       TEXT UNIQUE NOT NULL,
                password    TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )
        """)

        # Subjects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT UNIQUE NOT NULL
            )
        """)

        # Study sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL,
                subject_id   INTEGER NOT NULL,
                duration     INTEGER NOT NULL,
                notes        TEXT,
                session_date TEXT NOT NULL,
                FOREIGN KEY (user_id)    REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE RESTRICT
            )
        """)

        # Habits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                name       TEXT NOT NULL,
                streak     INTEGER DEFAULT 0,
                last_done  TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Goals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                title       TEXT NOT NULL,
                category    TEXT,
                progress    INTEGER DEFAULT 0,
                target_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        print("Database tables initialized successfully")

    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        raise

    finally:
        conn.close()


