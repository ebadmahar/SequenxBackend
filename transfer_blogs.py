import sqlite3

conn = sqlite3.connect("Backend/app.db")
cursor = conn.cursor()

cursor.execute("SELECT id, name, email FROM users WHERE email = 'editor.ahmed@example.com'")
editor = cursor.fetchone()
print("Editor user:", editor)

if editor:
    editor_id = editor[0]
    cursor.execute("UPDATE blog_posts SET author_id = ?", (editor_id,))
    print(f"Transferred all blogs to author_id {editor_id} ({editor[1]} - {editor[2]})")

# Also ensure exactly one post is featured
cursor.execute("SELECT id FROM blog_posts WHERE featured = 1")
featured_posts = cursor.fetchall()
print("Currently featured posts:", featured_posts)
if len(featured_posts) > 1:
    keep_id = featured_posts[0][0]
    cursor.execute("UPDATE blog_posts SET featured = 0 WHERE id != ?", (keep_id,))
    print(f"Set only post id {keep_id} as featured")
elif len(featured_posts) == 0:
    cursor.execute("UPDATE blog_posts SET featured = 1 WHERE id = 1")
    print("Set post id 1 as featured")

conn.commit()

cursor.execute("SELECT id, title, author_id, featured FROM blog_posts")
for row in cursor.fetchall():
    print(row)

conn.close()

