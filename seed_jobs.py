import sqlite3
from datetime import datetime

jobs = [
    {
        "title": "Software Engineer (Python)",
        "department": "Engineering",
        "location": "Islamabad, Pakistan / Remote",
        "job_type": "full_time",
        "status": "open",
        "description": "Join our backend team to build scalable and high-performance systems using Python, FastAPI, and asynchronous architectures.",
        "requirements": "3+ years experience with Python, FastAPI/Django, PostgreSQL, Redis, Docker, and AWS/GCP.",
    },
    {
        "title": "Senior Frontend Engineer (React/Next.js)",
        "department": "Engineering",
        "location": "Amsterdam, Netherlands / Remote",
        "job_type": "full_time",
        "status": "open",
        "description": "Architect modern, responsive web experiences using React 19, Next.js, and TypeScript for European enterprise clients.",
        "requirements": "4+ years experience with React, Next.js, modern CSS, WebGL/Three.js familiarity is a plus.",
    },
    {
        "title": "QA Automation Engineer",
        "department": "Quality Assurance",
        "location": "Lahore, Pakistan",
        "job_type": "full_time",
        "status": "open",
        "description": "Design robust automated end-to-end and regression testing frameworks using Playwright, Cypress, and CI/CD pipelines.",
        "requirements": "3+ years in QA automation, experience with Playwright/Selenium, Python or TypeScript.",
    },
]

conn = sqlite3.connect("Backend/app.db")
cursor = conn.cursor()
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for j in jobs:
    cursor.execute("SELECT id FROM jobs WHERE title = ?", (j["title"],))
    if not cursor.fetchone():
        cursor.execute(
            """INSERT INTO jobs (title, department, location, job_type, description, requirements, status, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)""",
            (
                j["title"],
                j["department"],
                j["location"],
                j["job_type"],
                j["description"],
                j["requirements"],
                j["status"],
                now,
            ),
        )
        print(f"Inserted job: {j['title']}")

conn.commit()
conn.close()
print("Done seeding jobs.")

