from datetime import datetime, timedelta, timezone
import random
import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.application import Application, ApplicationStatus
from app.models.blog import BlogPost, PostStatus
from app.models.contact import ContactMessage
from app.models.job import Job, JobStatus, JobType
from app.models.pageview import PageView
from app.models.user import User, UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_demo_data(db: Session) -> None:
    """Populate database with comprehensive realistic demo data matching visual dashboards."""
    Base.metadata.create_all(bind=engine)

    # Check idempotency
    existing_check = db.query(User).filter(User.email == "editor.ahmed@example.com").first()
    if existing_check:
        logger.info("Demo data already present in database. Skipping seed.")
        return

    logger.info("Seeding realistic demo dataset...")
    now = datetime.now(timezone.utc)

    # 1. USERS (6 users: 2 admin, 2 hr, 2 editors)
    users_data = [
        {"name": "Super Administrator", "email": settings.FIRST_ADMIN_EMAIL, "role": UserRole.admin, "pwd": settings.FIRST_ADMIN_PASSWORD},
        {"name": "Sarah Jenkins", "email": "sarah.admin@example.com", "role": UserRole.admin, "pwd": "AdminPassword123!"},
        {"name": "Sarah Ahmed", "email": "hr.sarah@example.com", "role": UserRole.hr, "pwd": "HrPassword123!"},
        {"name": "David Miller", "email": "hr.david@example.com", "role": UserRole.hr, "pwd": "HrPassword123!"},
        {"name": "Ahmed Khan", "email": "editor.ahmed@example.com", "role": UserRole.editor, "pwd": "EditorPassword123!"},
        {"name": "Ayesha Noor", "email": "editor.ayesha@example.com", "role": UserRole.editor, "pwd": "EditorPassword123!"},
    ]

    users_map = {}
    for u in users_data:
        usr = db.query(User).filter(User.email == u["email"]).first()
        if not usr:
            usr = User(
                name=u["name"],
                email=u["email"],
                password_hash=get_password_hash(u["pwd"]),
                role=u["role"],
                is_active=True,
                created_at=now - timedelta(days=90),
            )
            db.add(usr)
            db.flush()
        users_map[u["email"]] = usr

    admin_usr = users_map[settings.FIRST_ADMIN_EMAIL]
    editor_ahmed = users_map["editor.ahmed@example.com"]
    editor_ayesha = users_map["editor.ayesha@example.com"]
    hr_sarah = users_map["hr.sarah@example.com"]

    # 2. BLOG POSTS (12 posts matching screenshots)
    posts_data = [
        {
            "title": "Future of AI in Pakistan",
            "slug": "future-of-ai-in-pakistan",
            "excerpt": "Exploring how AI is shaping industries, education, healthcare, and software exports.",
            "content": "Artificial Intelligence is transforming how we live and work in emerging markets. In Pakistan, we are seeing rapid adoption across education, healthcare, agriculture, and high-value tech services. Startups and established institutions alike are building generative models and computer vision pipelines to solve localized challenges.",
            "status": PostStatus.published,
            "views_count": 4200,
            "author_id": editor_ahmed.id,
            "published_at": now - timedelta(days=5),
            "created_at": now - timedelta(days=12),
        },
        {
            "title": "Remote Work Best Practices",
            "slug": "remote-work-best-practices",
            "excerpt": "Practical engineering strategies for asynchronous collaboration across global timezones.",
            "content": "Transitioning to effective remote work requires more than Slack channels and Zoom calls. Teams thrive when documentation is prioritized, meetings are replaced with well-scoped RFCs, and asynchronous communication habits are cultivated across engineering squads.",
            "status": PostStatus.published,
            "views_count": 3100,
            "author_id": editor_ahmed.id,
            "published_at": now - timedelta(days=10),
            "created_at": now - timedelta(days=15),
        },
        {
            "title": "How to Build Great Teams",
            "slug": "how-to-build-great-teams",
            "excerpt": "A deep dive into hiring culture, psychological safety, and empowering individual contributors.",
            "content": "High-performing teams are built on psychological safety, clarity of mission, and trust. Leaders must focus on eliminating blockers, mentoring emerging talent, and fostering peer accountability rather than micromanaging daily tasks.",
            "status": PostStatus.published,
            "views_count": 2800,
            "author_id": editor_ahmed.id,
            "published_at": now - timedelta(days=18),
            "created_at": now - timedelta(days=22),
        },
        {
            "title": "Cybersecurity in 2026",
            "slug": "cybersecurity-in-2026",
            "excerpt": "Anticipating automated vulnerability scanning, quantum-resistant crypto, and API protection.",
            "content": "Modern application security demands proactive posture management. Organizations are shifting left by integrating automated SAST/DAST into CI pipelines, enforcing zero trust networks, and securing microservice API boundaries with mutual TLS.",
            "status": PostStatus.pending_review,
            "views_count": 980,
            "author_id": editor_ahmed.id,
            "published_at": None,
            "created_at": now - timedelta(days=14),
        },
        {
            "title": "The Rise of Green Tech",
            "slug": "the-rise-of-green-tech",
            "excerpt": "How sustainable computing and energy efficiency are redefining cloud architectures.",
            "content": "Server optimization, efficient container schedulers, and renewable-powered data centers are no longer optional. Green engineering practices directly lower cloud bills and corporate carbon footprints.",
            "status": PostStatus.published,
            "views_count": 1900,
            "author_id": editor_ayesha.id,
            "published_at": now - timedelta(days=20),
            "created_at": now - timedelta(days=25),
        },
        {
            "title": "Sustainable Tech Trends",
            "slug": "sustainable-tech-trends",
            "excerpt": "Emerging hardware lifecycles and clean tech software solutions for the decade ahead.",
            "content": "Circular economics in consumer electronics, edge sensor telemetry for climate modeling, and battery management platforms represent the next frontier of impactful software development.",
            "status": PostStatus.draft,
            "views_count": 1200,
            "author_id": editor_ayesha.id,
            "published_at": None,
            "created_at": now - timedelta(days=9),
        },
        {
            "title": "Mastering Cloud Native Infrastructure",
            "slug": "mastering-cloud-native-infrastructure",
            "excerpt": "Architecting resilient Kubernetes clusters and declarative GitOps pipelines.",
            "content": "Declarative infrastructure as code enables autonomous rollouts, instant rollbacks, and reproducible multi-region staging environments that scale seamlessly under production workloads.",
            "status": PostStatus.published,
            "views_count": 2450,
            "author_id": admin_usr.id,
            "published_at": now - timedelta(days=25),
            "created_at": now - timedelta(days=30),
        },
        {
            "title": "Effective API Design Patterns",
            "slug": "effective-api-design-patterns",
            "excerpt": "REST, RPC, and GraphQL best practices for robust public and partner interfaces.",
            "content": "Consistent status codes, idempotent write handlers, clear schema documentation, and backward-compatible versioning guarantee developer happiness and reduce integration cycle times.",
            "status": PostStatus.published,
            "views_count": 1820,
            "author_id": editor_ahmed.id,
            "published_at": now - timedelta(days=28),
            "created_at": now - timedelta(days=35),
        },
        {
            "title": "Building Resilient Distributed Systems",
            "slug": "building-resilient-distributed-systems",
            "excerpt": "Handling network partitions, backpressure, and graceful degradation under load.",
            "content": "Circuit breakers, rate limits, retry backoffs with jitter, and dead letter queues ensure systems bend gracefully rather than catastrophic cascade outages.",
            "status": PostStatus.published,
            "views_count": 3400,
            "author_id": admin_usr.id,
            "published_at": now - timedelta(days=35),
            "created_at": now - timedelta(days=40),
        },
        {
            "title": "Modern Frontend Performance",
            "slug": "modern-frontend-performance",
            "excerpt": "Core Web Vitals, code splitting, and edge caching for sub-second interactions.",
            "content": "Tree-shaking unused dependencies, streaming SSR, and modern image formats directly elevate user retention and conversion metrics across enterprise platforms.",
            "status": PostStatus.draft,
            "views_count": 650,
            "author_id": editor_ahmed.id,
            "published_at": None,
            "created_at": now - timedelta(days=4),
        },
        {
            "title": "UX Principles for Enterprise Software",
            "slug": "ux-principles-for-enterprise-software",
            "excerpt": "Simplifying complex B2B workflows without sacrificing power or density.",
            "content": "Enterprise users value density, speed, keyboard accessibility, and predictable layouts over flashy animations. Clear hierarchy and high-contrast cues keep teams productive.",
            "status": PostStatus.pending_review,
            "views_count": 450,
            "author_id": editor_ayesha.id,
            "published_at": None,
            "created_at": now - timedelta(days=2),
        },
        {
            "title": "Zero Trust Security Implementation",
            "slug": "zero-trust-security-implementation",
            "excerpt": "Never trust, always verify: enforcing continuous identity assertion.",
            "content": "Perimeter security is obsolete. Modern systems enforce continuous identity verification, least-privilege scoping, and strict device health checks for every single internal API call.",
            "status": PostStatus.published,
            "views_count": 1560,
            "author_id": admin_usr.id,
            "published_at": now - timedelta(days=45),
            "created_at": now - timedelta(days=50),
        },
    ]

    for p in posts_data:
        post = BlogPost(**p)
        db.add(post)
    db.flush()

    # 3. JOBS (8 positions matching screenshots)
    jobs_data = [
        {"title": "Software Engineer", "department": "Engineering", "location": "Remote", "job_type": JobType.full_time, "status": JobStatus.open, "deadline": now + timedelta(days=30)},
        {"title": "Product Manager", "department": "Product", "location": "Islamabad", "job_type": JobType.full_time, "status": JobStatus.open, "deadline": now + timedelta(days=25)},
        {"title": "Content Writer", "department": "Marketing", "location": "Remote", "job_type": JobType.part_time, "status": JobStatus.open, "deadline": now + timedelta(days=15)},
        {"title": "UX Designer", "department": "Design", "location": "Hybrid", "job_type": JobType.full_time, "status": JobStatus.closed, "deadline": now - timedelta(days=2)},
        {"title": "HR Executive", "department": "HR", "location": "Islamabad", "job_type": JobType.full_time, "status": JobStatus.open, "deadline": now + timedelta(days=20)},
        {"title": "DevOps Specialist", "department": "Engineering", "location": "Remote", "job_type": JobType.contract, "status": JobStatus.open, "deadline": now + timedelta(days=40)},
        {"title": "Frontend Developer", "department": "Engineering", "location": "Remote", "job_type": JobType.full_time, "status": JobStatus.open, "deadline": now + timedelta(days=35)},
        {"title": "Data Analyst", "department": "Analytics", "location": "Hybrid", "job_type": JobType.full_time, "status": JobStatus.open, "deadline": now + timedelta(days=18)},
    ]

    jobs_map = {}
    for j in jobs_data:
        job = Job(
            title=j["title"],
            department=j["department"],
            location=j["location"],
            job_type=j["job_type"],
            description=f"We are looking for an experienced {j['title']} to join our growing organization. In this role, you will collaborate with cross-functional teams to build and scale exceptional digital products.",
            requirements="3+ years of relevant industry experience, strong communication skills, demonstrated problem-solving ability, and alignment with our collaborative culture.",
            status=j["status"],
            deadline=j["deadline"],
            created_by=hr_sarah.id,
            created_at=now - timedelta(days=45),
        )
        db.add(job)
        db.flush()
        jobs_map[j["title"]] = job

    # 4. APPLICATIONS (25 applications matching screenshots)
    apps_data = [
        # Software Engineer (8 apps)
        ("Ali Raza", "ali.raza@example.com", "+92-300-1122334", "Software Engineer", ApplicationStatus.new, 1),
        ("Bilal Tariq", "bilal.t@example.com", "+92-301-4455667", "Software Engineer", ApplicationStatus.shortlisted, 3),
        ("Hamza Farooq", "hamza.f@example.com", "+92-302-7788990", "Software Engineer", ApplicationStatus.hired, 5),
        ("Zainab Malik", "zainab.m@example.com", "+92-303-1234567", "Software Engineer", ApplicationStatus.reviewed, 7),
        ("Omar Siddiqui", "omar.s@example.com", "+92-304-7654321", "Software Engineer", ApplicationStatus.rejected, 10),
        ("Sana Mir", "sana.mir@example.com", "+92-305-9988776", "Software Engineer", ApplicationStatus.new, 12),
        ("Danial Sheikh", "danial.s@example.com", "+92-306-3344556", "Software Engineer", ApplicationStatus.reviewed, 16),
        ("Zeeshan Ali", "zeeshan.a@example.com", "+92-307-5566778", "Software Engineer", ApplicationStatus.new, 20),

        # Product Manager (5 apps)
        ("Ayesha Khan", "ayesha@example.com", "+92-311-2233445", "Product Manager", ApplicationStatus.reviewed, 2),
        ("Sarah Nadeem", "sarah.n@example.com", "+92-312-3344556", "Product Manager", ApplicationStatus.shortlisted, 6),
        ("Fahad Qureshi", "fahad.q@example.com", "+92-313-4455667", "Product Manager", ApplicationStatus.reviewed, 11),
        ("Nida Aslam", "nida.a@example.com", "+92-314-5566778", "Product Manager", ApplicationStatus.new, 15),
        ("Taimoor Shah", "taimoor.s@example.com", "+92-315-6677889", "Product Manager", ApplicationStatus.rejected, 22),

        # Content Writer (4 apps)
        ("Hassan Ali", "hassan@example.com", "+92-321-9988776", "Content Writer", ApplicationStatus.shortlisted, 2),
        ("Rabia Basri", "rabia.b@example.com", "+92-322-1122334", "Content Writer", ApplicationStatus.reviewed, 8),
        ("Asad Mehmood", "asad.m@example.com", "+92-323-2233445", "Content Writer", ApplicationStatus.new, 14),
        ("Kashif Riaz", "kashif.r@example.com", "+92-324-3344556", "Content Writer", ApplicationStatus.shortlisted, 19),

        # UX Designer (3 apps)
        ("Mariam Butt", "mariam@example.com", "+92-331-5566778", "UX Designer", ApplicationStatus.new, 2),
        ("Alizeh Fatima", "alizeh.f@example.com", "+92-332-6677889", "UX Designer", ApplicationStatus.reviewed, 9),
        ("Muneeb Ur Rehman", "muneeb.r@example.com", "+92-333-7788990", "UX Designer", ApplicationStatus.shortlisted, 17),

        # HR Executive (2 apps)
        ("Usman Tariq", "usman@example.com", "+92-341-8899001", "HR Executive", ApplicationStatus.reviewed, 2),
        ("Mahnoor Jahangir", "mahnoor.j@example.com", "+92-342-9900112", "HR Executive", ApplicationStatus.new, 13),

        # Others (3 apps)
        ("Kamran Akmal", "kamran.a@example.com", "+92-351-1122445", "DevOps Specialist", ApplicationStatus.new, 4),
        ("Hina Dilpazir", "hina.d@example.com", "+92-352-2233556", "Frontend Developer", ApplicationStatus.shortlisted, 8),
        ("Waleed Jameel", "waleed.j@example.com", "+92-353-3344667", "Data Analyst", ApplicationStatus.reviewed, 18),
    ]

    for name, email, phone, job_title, st, days_ago in apps_data:
        target_job = jobs_map[job_title]
        app = Application(
            job_id=target_job.id,
            full_name=name,
            email=email,
            phone=phone,
            cover_note=f"Dear Hiring Team,\n\nI am thrilled to apply for the {job_title} position. With my relevant background and passion for excellence, I look forward to contributing to your vision.",
            cv_path="uploads/cvs/sample_cv.pdf",
            status=st,
            created_at=now - timedelta(days=days_ago),
        )
        db.add(app)
    db.flush()

    # 5. CONTACT MESSAGES (15 messages matching screenshot)
    messages_data = [
        ("Zara Ali", "zara.ali@example.com", "Partnership Opportunity", "Hello,\n\nI am reaching out to explore potential partnership opportunities between our organizations. We are impressed by your work and would like to discuss possible collaboration.", False, 0),
        ("Bilal Ahmed", "bilal.ahmed@example.com", "Inquiry about services", "Good afternoon. We are currently evaluating cloud migration consulting partners. Could you share your enterprise portfolio and pricing structure?", False, 1),
        ("Fatima Khan", "fatima.khan@example.com", "Job application inquiry", "Hi Team, I submitted an application for the UX Designer opening and wanted to confirm if additional design portfolio links are required.", False, 2),
        ("Imran Sheikh", "imran.s@example.com", "Collaboration", "We are hosting an annual software leadership symposium and would be honored to invite a keynote speaker from your engineering team.", False, 2),
        ("Amna Malik", "amna.malik@example.com", "General inquiry", "Hello, do you offer customized corporate training sessions for cloud infrastructure and site reliability engineering?", False, 4),
        ("Saad Rafiq", "saad.r@example.com", "Enterprise Consultation", "We need an assessment on distributed systems resilience for a fintech platform. Please let us know availability for a discovery call.", True, 0),
        ("Maria Qasim", "maria.q@example.com", "Product demo request", "Could you arrange a quick walkthrough of your analytics platform for our executive committee next Tuesday?", True, 1),
        ("Farhan Akhtar", "farhan.a@example.com", "Vendor partnership", "Proposing an affiliate technology partnership in digital payments integration.", True, 2),
        ("Hira Mani", "hira.m@example.com", "Press & Media query", "Writing a feature story on emerging technology firms and would love an interview with your leadership.", True, 3),
        ("Salman Iqbal", "salman.i@example.com", "Investment query", "Reaching out from a regional venture syndicate to learn more about your upcoming strategic expansion rounds.", True, 4),
        ("Aftab Shivdasani", "aftab.s@example.com", "Security disclosure", "Responsible disclosure report regarding an informative HTTP header on the staging sub-domain.", False, 8),
        ("Sonya Hussyn", "sonya.h@example.com", "Speaking invitation", "Invitation to participate in the Women in Tech Leadership Panel next month.", False, 12),
        ("Sheheryar Munawar", "sheheryar.m@example.com", "Careers query", "Are there internship opportunities available for graduate students in computer science?", False, 16),
        ("Maya Ali", "maya.ali@example.com", "Case study request", "Requesting permission to reference your green tech deployment architecture in our academic research paper.", False, 22),
        ("Humayun Saeed", "humayun.s@example.com", "Corporate Training", "Inquiring about executive workshops on AI adoption frameworks.", False, 27),
    ]

    for name, email, subj, msg, is_read, days_ago in messages_data:
        c_msg = ContactMessage(
            name=name,
            email=email,
            subject=subj,
            message=msg,
            is_read=is_read,
            created_at=now - timedelta(days=days_ago),
        )
        db.add(c_msg)
    db.flush()

    # 6. PAGE VIEWS (30 days of realistic website traffic total ~12,548)
    daily_views_distribution = [
        380, 410, 435, 395, 420, 460, 415,
        440, 410, 430, 455, 470, 425, 410,
        435, 440, 465, 450, 420, 435, 460,
        480, 470, 445, 460, 450, 440, 465,
        450, 433,
    ]  # sum is approx 13,000

    sample_paths = [
        ("/", None),
        ("/blog", None),
        ("/jobs", None),
        ("/contact", None),
        ("/blog/future-of-ai-in-pakistan", "future-of-ai-in-pakistan"),
        ("/blog/remote-work-best-practices", "remote-work-best-practices"),
        ("/blog/how-to-build-great-teams", "how-to-build-great-teams"),
        ("/blog/the-rise-of-green-tech", "the-rise-of-green-tech"),
        ("/blog/mastering-cloud-native-infrastructure", "mastering-cloud-native-infrastructure"),
    ]

    referrers = ["https://google.com", "https://linkedin.com", "https://twitter.com", "https://news.ycombinator.com", None]

    pv_batch = []
    for day_idx, daily_count in enumerate(daily_views_distribution):
        target_day = now - timedelta(days=29 - day_idx)
        for _ in range(daily_count):
            path_item, blog_slug = random.choice(sample_paths)
            random_second = random.randint(0, 86399)
            pv_time = target_day.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(seconds=random_second)

            pv = PageView(
                path=path_item,
                blog_slug=blog_slug,
                referrer=random.choice(referrers),
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                ip_address=f"192.168.1.{random.randint(10, 250)}",
                created_at=pv_time,
            )
            pv_batch.append(pv)

            if len(pv_batch) >= 1000:
                db.bulk_save_objects(pv_batch)
                pv_batch = []

    if pv_batch:
        db.bulk_save_objects(pv_batch)

    db.commit()
    logger.info("Successfully seeded demo data: 6 users, 12 blog posts, 8 jobs, 25 applications, 15 messages, and 30 days of traffic.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
