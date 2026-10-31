import sqlite3
from datetime import datetime

posts = [
    {
        "id": 1,
        "slug": "building-high-performance-remote-development-teams",
        "title": "Building High-Performance Remote Development Teams",
        "excerpt": "Discover best practices, tools, and strategies for building and managing high-performing remote development teams in today's global environment.",
        "category": "Remote Teams",
        "cover_image": "/images/blog/remote-dev.jpg",
        "read_time": "8 min read",
        "featured": 1,
        "tags": "Remote Work, Team Culture, Best Practices",
        "views_count": 1420,
        "author_name": "Ali Raza",
        "author_role": "Senior Engineering Manager",
        "author_avatar": "/images/blog/author-ali.jpg",
        "author_bio": "Ali leads engineering teams at SeQuenX with a focus on building scalable software solutions and high-performing remote teams. He has over 8 years of experience in software development, team leadership, and cloud technologies.",
        "content": """<h2>Introduction</h2>
<p>Remote development teams have become a key driver of innovation and growth for modern businesses. With the right strategy, tools, and culture, distributed teams can be just as productive—if not more—than traditional in-house teams. At SeQuenX, we have helped multiple organizations build and scale high-performing remote teams, and in this article, we share the lessons learned and best practices that make a real difference.</p>

<h2>1. Define Clear Goals and Expectations</h2>
<p>A successful remote team starts with clarity. Define project goals, individual responsibilities, and success metrics from day one. This ensures everyone is aligned and understands how their work contributes to the bigger picture.</p>

<div class="blog-quote-box">
  <p>"Clear communication and well-defined expectations remove ambiguity and empower teams to perform at their best."</p>
</div>

<h2>2. Use the Right Tools</h2>
<p>The right tools enable seamless collaboration, transparent communication, and efficient project management. Some of the essential tools for remote development teams include:</p>

<div class="blog-tools-grid">
  <div class="blog-tool-item">
    <strong>Communication</strong>
    <span>Slack, Microsoft Teams</span>
  </div>
  <div class="blog-tool-item">
    <strong>Project Management</strong>
    <span>Jira, ClickUp, Linear</span>
  </div>
  <div class="blog-tool-item">
    <strong>Version Control</strong>
    <span>Git, GitHub Enterprise</span>
  </div>
  <div class="blog-tool-item">
    <strong>Documentation</strong>
    <span>Confluence, Notion</span>
  </div>
</div>

<h2>3. Foster a Strong Team Culture</h2>
<p>Even in a remote setup, culture matters. Encourage regular team check-ins, virtual social events, and open communication. Recognize achievements and create opportunities for professional growth.</p>

<h2>Conclusion</h2>
<p>Building a high-performing remote development team is not just about tools — it is about people, processes, and culture.</p>""",
    },
    {
        "id": 2,
        "slug": "how-ai-is-transforming-business-operations",
        "title": "How AI is Transforming Business Operations",
        "excerpt": "Explore real-world use cases of AI in modern businesses, from workflow automation to predictive analytics and intelligent customer support.",
        "category": "AI & Innovation",
        "cover_image": "/images/blog/ai-transform.png",
        "read_time": "6 min read",
        "featured": 0,
        "tags": "AI, Innovation, Best Practices",
        "views_count": 980,
        "author_name": "Shurjeel Tousif",
        "author_role": "AI Solutions Lead",
        "author_avatar": "/images/team/shurjeel-tousif.jpg",
        "author_bio": "Shurjeel works on enterprise intelligence systems, LLM integrations, and machine learning pipelines.",
        "content": """<h2>Automating Complex Workflows</h2>
<p>Artificial Intelligence is no longer just a research experiment; it is deeply embedded into day-to-day business operations. Companies using AI in document processing, automated triage, and predictive forecasting achieve up to 40% efficiency gains.</p>""",
    },
    {
        "id": 3,
        "slug": "nextjs-15-whats-new-and-why-it-matters",
        "title": "Next.js 15: What's New and Why It Matters",
        "excerpt": "A practical overview of the latest features in Next.js and how they improve developer productivity, server actions, and runtime speed.",
        "category": "Software Development",
        "cover_image": "/images/blog/remote-dev.jpg",
        "read_time": "5 min read",
        "featured": 0,
        "tags": "Next.js, React, Cloud",
        "views_count": 810,
        "author_name": "Ahmed Khan",
        "author_role": "Lead Frontend Architect",
        "author_avatar": "/images/team/shurjeel-tousif.jpg",
        "author_bio": "Ahmed specializes in React architecture, server components, and enterprise web performance.",
        "content": """<h2>Turbopack by Default and Async Request APIs</h2>
<p>Next.js continues to mature into the premier React framework for fullstack web applications. With asynchronous request handling for headers and cookies, plus faster incremental builds via Turbopack, developer velocity is higher than ever.</p>""",
    },
    {
        "id": 4,
        "slug": "10-tips-for-effective-remote-team-collaboration",
        "title": "10 Tips for Effective Remote Team Collaboration",
        "excerpt": "Learn how to keep your remote team aligned, productive, motivated, and engaged across different international time zones.",
        "category": "Remote Teams",
        "cover_image": "/images/blog/remote-collab.png",
        "read_time": "6 min read",
        "featured": 0,
        "tags": "Remote Work, Team Culture",
        "views_count": 650,
        "author_name": "Ali Raza",
        "author_role": "Senior Engineering Manager",
        "author_avatar": "/images/blog/author-ali.jpg",
        "author_bio": "Ali leads engineering teams at SeQuenX with a focus on building scalable software solutions.",
        "content": """<h2>Asynchronous Communication First</h2>
<p>When working across time zones, default to written asynchronous documentation rather than meetings. Write clear pull request descriptions, update task statuses in Jira, and record short video walkthroughs when reviewing code.</p>""",
    },
    {
        "id": 5,
        "slug": "life-at-sequenx-people-growth-and-impact",
        "title": "Life at SeQuenX: People, Growth and Impact",
        "excerpt": "A look inside our culture, values, and what makes SeQuenX a great place to build your career and work on global tech projects.",
        "category": "Career & Culture",
        "cover_image": "/images/blog/culture-growth.jpg",
        "read_time": "4 min read",
        "featured": 0,
        "tags": "Team Culture, Innovation",
        "views_count": 520,
        "author_name": "Sana Ali",
        "author_role": "People & Culture Director",
        "author_avatar": "/images/team/sana-ali.jpg",
        "author_bio": "Sana fosters human talent, learning environments, and employee well-being across SeQuenX global offices.",
        "content": """<h2>Empowering Engineers to Make Impact</h2>
<p>At SeQuenX, we cultivate curiosity, mutual respect, and continuous learning. We invest in team certifications, provide mentorship programs, and celebrate every project milestone together.</p>""",
    },
    {
        "id": 6,
        "slug": "scalable-architecture-on-the-cloud",
        "title": "Scalable Architecture on the Cloud",
        "excerpt": "Key considerations and best practices for building scalable, secure, and cost-efficient cloud solutions on AWS, Azure, and Google Cloud.",
        "category": "Software Development",
        "cover_image": "/images/blog/cloud-arch.png",
        "read_time": "7 min read",
        "featured": 0,
        "tags": "Cloud, Security, Architecture",
        "views_count": 730,
        "author_name": "Zier den Heijer",
        "author_role": "Chief Technology Architect",
        "author_avatar": "/images/team/zier-den-heijer.jpg",
        "author_bio": "Zier brings decades of enterprise consulting experience guiding high-volume distributed systems.",
        "content": """<h2>Designing for High Availability and Disaster Recovery</h2>
<p>True scalability begins with stateless services, distributed caching layers, and multi-region failover automation. We explore zero-downtime deployment strategies that enterprise leaders rely on.</p>""",
    },
    {
        "id": 7,
        "slug": "sequenx-expands-global-delivery-capabilities",
        "title": "SeQuenX Expands Global Delivery Capabilities",
        "excerpt": "We are excited to announce the expansion of our delivery centers and new engineering partnerships to better serve our enterprise clients.",
        "category": "Company News",
        "cover_image": "/images/blog/global-delivery.jpg",
        "read_time": "4 min read",
        "featured": 0,
        "tags": "Case Study, Innovation",
        "views_count": 410,
        "author_name": "Ebad Rahman",
        "author_role": "Managing Director",
        "author_avatar": "/images/team/zier-den-heijer.jpg",
        "author_bio": "Ebad drives strategic expansion, client partnerships, and technological vision at SeQuenX.",
        "content": """<h2>Expanding International Presence</h2>
<p>With increasing demand for specialized software engineering and OSS governance, SeQuenX has expanded its delivery capabilities, establishing deeper ties between the European tech corridor and global engineering hubs.</p>""",
    },
]

conn = sqlite3.connect("Backend/app.db")
cursor = conn.cursor()

now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

for p in posts:
    cursor.execute("SELECT id FROM blog_posts WHERE slug = ?", (p["slug"],))
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(
            """INSERT INTO blog_posts
            (title, slug, excerpt, content, cover_image, category, tags, read_time, featured, status, views_count, author_id, author_name, author_role, author_avatar, author_bio, published_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'published', ?, 1, ?, ?, ?, ?, ?, ?)""",
            (
                p["title"],
                p["slug"],
                p["excerpt"],
                p["content"],
                p["cover_image"],
                p["category"],
                p["tags"],
                p["read_time"],
                p["featured"],
                p["views_count"],
                p["author_name"],
                p["author_role"],
                p["author_avatar"],
                p["author_bio"],
                now,
                now,
            ),
        )
        print(f"Inserted: {p['title']}")
    else:
        cursor.execute(
            """UPDATE blog_posts SET
                category = ?, tags = ?, read_time = ?, featured = ?,
                author_name = ?, author_role = ?, author_avatar = ?, author_bio = ?,
                status = 'published', published_at = coalesce(published_at, ?)
            WHERE slug = ?""",
            (
                p["category"],
                p["tags"],
                p["read_time"],
                p["featured"],
                p["author_name"],
                p["author_role"],
                p["author_avatar"],
                p["author_bio"],
                now,
                p["slug"],
            ),
        )
        print(f"Updated: {p['title']}")

conn.commit()
conn.close()
print("Done seeding blogs.")

