import sqlite3

db = sqlite3.connect("study.db")
cursor = db.cursor()

subjects = [
    "Mathematics",
    "Biology",
    "Physics",
    "Computer Science",
    "Art",
    "Music",
    "Literature",
    "Philosophy",
    "Economics",
    "Psychology",
    "Sociology",
    "Geography",
    "English",
    "History",
    "Chemistry",
]

for subj in subjects:
    try:
        cursor.execute("INSERT INTO subjects (name) VALUES (?)", (subj,))
    except sqlite3.IntegrityError:
        pass  # already exists

db.commit()
db.close()

print("Subjects added or already existed")