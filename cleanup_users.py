import sqlite3

conn = sqlite3.connect("Backend/app.db")
cursor = conn.cursor()

# Delete non-admin accounts
cursor.execute("DELETE FROM users WHERE email IN ('hr.sarah@example.com', 'editor.ahmed@example.com')")
conn.commit()

cursor.execute("SELECT id, name, email, role FROM users")
print("Remaining users:", cursor.fetchall())

conn.close()

