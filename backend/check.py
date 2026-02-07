import sqlite3

conn = sqlite3.connect("study.db")
cursor = conn.cursor()

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
rows = cursor.fetchall()

if rows:
    print("Subjects found:")
    for row in rows:
        print(f"ID {row[0]}: {row[1]}")
else:
    print("No subjects in the database yet.")

conn.close()