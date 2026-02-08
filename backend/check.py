import sqlite3

conn = sqlite3.connect("study.db")
cursor = conn.cursor()

try:
    cursor.execute("SELECT id, name FROM subjects ORDER BY name")
    rows = cursor.fetchall()
    
    if rows:
        print("Found subjects:")
        for row in rows:
            print(f"  ID {row[0]} → {row[1]}")
    else:
        print("No subjects found in the table (but table exists)")
except sqlite3.OperationalError as e:
    if "no such table" in str(e):
        print("Subjects table does NOT exist yet.")
    else:
        print("Error:", e)

conn.close()