"""
Database cleanup script.
Removes all demo/seed business data while keeping 3 staff accounts.
Run once from the Backend/ directory: python cleanup_demo_data.py
"""
import sqlite3
import shutil
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')
BACKUP_PATH = DB_PATH + '.backup'

# Step 1: Backup
if not os.path.exists(BACKUP_PATH):
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"Backup created: {BACKUP_PATH}")
else:
    print(f"Backup already exists: {BACKUP_PATH}")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Step 2: Keep only 3 staff accounts; delete the rest
KEEP_EMAILS = ('admin@example.com', 'hr.sarah@example.com', 'editor.ahmed@example.com')
placeholders = ','.join('?' for _ in KEEP_EMAILS)
c.execute(f"DELETE FROM users WHERE email NOT IN ({placeholders})", KEEP_EMAILS)
print(f"Deleted {c.rowcount} extra user account(s)")

# Step 3: Clear all demo business data tables
for table in ['page_views', 'applications', 'blog_posts', 'jobs', 'contact_messages']:
    c.execute(f"DELETE FROM {table}")
    print(f"Cleared {c.rowcount} rows from {table}")

# Step 4: Keep settings (hr_email etc)
conn.commit()

# Step 5: Verify
print("\nRemaining users:")
c.execute("SELECT id, name, email, role FROM users ORDER BY id")
for row in c.fetchall():
    print(f"  {row}")

conn.close()
print("\nDatabase cleanup complete.")

