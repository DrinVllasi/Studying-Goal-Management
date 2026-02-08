import sqlite3

conn = sqlite3.connect("study.db")
cursor = conn.cursor()

subjects = [
    "Mathematics",
    "Programming",
    "Art",
    "Music",
    "Philosophy",
    "Economics",
    "Psychology",
    "Sociology",
    "Biology",
    "Physics",
    "Geography",
    "English",
    "History",
    "Chemistry",
    "Literature",
    "Computer Science",
]

for name in subjects:
    try:
        cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
        print(f"Added: {name}")
    except sqlite3.IntegrityError:
        print(f"Already exists: {name}")

conn.commit()
conn.close()

print("Done.")