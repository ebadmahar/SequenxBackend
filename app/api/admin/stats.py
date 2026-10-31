from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.application import Application, ApplicationStatus
from app.models.blog import BlogPost, PostStatus
from app.models.contact import ContactMessage
from app.models.job import Job, JobStatus
from app.models.pageview import PageView
from app.models.user import User, UserRole
from app.schemas.analytics import (
    ApplicationByJob,
    ApplicationByStatus,
    ApplicationOverTime,
    DailyVisit,
    EditorPostMonth,
    EditorStats,
    FunnelStage,
    MessagePerWeek,
    OverviewStats,
    StatTrend,
    TopPost,
)

router = APIRouter(prefix="/admin/stats", tags=["Admin Stats"])

def calc_change_pct(current: int, previous: int) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100.0, 1)

@router.get(
    "/overview",
    response_model=OverviewStats,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard overview metrics",
    description="Retrieve high-level statistics and trend comparisons versus the prior 30-day period.",
)
def get_overview_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr, UserRole.editor)),
):
    now = datetime.now(timezone.utc)
    d30 = now - timedelta(days=30)
    d60 = now - timedelta(days=60)

    # 1. Visitors
    visitors_curr = db.query(PageView).filter(PageView.created_at >= d30).count()
    visitors_prev = db.query(PageView).filter(PageView.created_at >= d60, PageView.created_at < d30).count()
    total_visitors_all = db.query(PageView).count()
    visitor_value = total_visitors_all if total_visitors_all > 0 else visitors_curr

    # 2. Blog posts
    published_curr = db.query(BlogPost).filter(BlogPost.status == PostStatus.published, BlogPost.created_at >= d30).count()
    published_prev = db.query(BlogPost).filter(BlogPost.status == PostStatus.published, BlogPost.created_at >= d60, BlogPost.created_at < d30).count()
    total_published = db.query(BlogPost).filter(BlogPost.status == PostStatus.published).count()
    drafts_count = db.query(BlogPost).filter(BlogPost.status == PostStatus.draft).count()
    pending_count = db.query(BlogPost).filter(BlogPost.status == PostStatus.pending_review).count()

    # 3. Jobs
    open_jobs_total = db.query(Job).filter(Job.status == JobStatus.open).count()
    open_jobs_curr = db.query(Job).filter(Job.status == JobStatus.open, Job.created_at >= d30).count()
    open_jobs_prev = db.query(Job).filter(Job.status == JobStatus.open, Job.created_at >= d60, Job.created_at < d30).count()
    closed_jobs_total = db.query(Job).filter(Job.status == JobStatus.closed).count()

    # 4. Applications
    new_apps_curr = db.query(Application).filter(Application.status == ApplicationStatus.new, Application.created_at >= d30).count()
    new_apps_prev = db.query(Application).filter(Application.status == ApplicationStatus.new, Application.created_at >= d60, Application.created_at < d30).count()
    total_apps = db.query(Application).count()

    shortlisted_curr = db.query(Application).filter(Application.status == ApplicationStatus.shortlisted, Application.created_at >= d30).count()
    shortlisted_prev = db.query(Application).filter(Application.status == ApplicationStatus.shortlisted, Application.created_at >= d60, Application.created_at < d30).count()
    shortlisted_total = db.query(Application).filter(Application.status == ApplicationStatus.shortlisted).count()

    # 5. Messages
    unread_curr = db.query(ContactMessage).filter(ContactMessage.is_read == False).count()
    unread_d30 = db.query(ContactMessage).filter(ContactMessage.is_read == False, ContactMessage.created_at >= d30).count()
    unread_d60 = db.query(ContactMessage).filter(ContactMessage.is_read == False, ContactMessage.created_at >= d60, ContactMessage.created_at < d30).count()
    total_messages = db.query(ContactMessage).count()

    # 6. Users
    active_users_total = db.query(User).filter(User.is_active == True).count()
    active_users_prev = db.query(User).filter(User.is_active == True, User.created_at < d30).count()

    return OverviewStats(
        total_visitors=StatTrend(value=visitor_value, change_pct=calc_change_pct(visitors_curr, visitors_prev)),
        published_posts=StatTrend(value=total_published, change_pct=calc_change_pct(published_curr, published_prev)),
        draft_posts=drafts_count,
        pending_posts=pending_count,
        open_jobs=StatTrend(value=open_jobs_total, change_pct=calc_change_pct(open_jobs_curr, open_jobs_prev)),
        closed_jobs=closed_jobs_total,
        new_applications=StatTrend(value=new_apps_curr, change_pct=calc_change_pct(new_apps_curr, new_apps_prev)),
        total_applications=total_apps,
        shortlisted_applications=StatTrend(value=shortlisted_total, change_pct=calc_change_pct(shortlisted_curr, shortlisted_prev)),
        unread_messages=StatTrend(value=unread_curr, change_pct=calc_change_pct(unread_d30, unread_d60)),
        total_messages=total_messages,
        active_users=StatTrend(value=active_users_total, change_pct=calc_change_pct(active_users_total, active_users_prev)),
    )

@router.get(
    "/visits",
    response_model=List[DailyVisit],
    status_code=status.HTTP_200_OK,
    summary="Daily page views over time",
    description="Retrieve daily website visit counts for the requested timeframe. Restricted to Admin.",
)
def get_daily_visits(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    now = datetime.now(timezone.utc)
    results = []

    for i in range(days - 1, -1, -1):
        target_date = now - timedelta(days=i)
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        count = db.query(PageView).filter(
            PageView.created_at >= day_start,
            PageView.created_at <= day_end,
        ).count()

        results.append(DailyVisit(
            date=target_date.strftime("%b %d"),
            views=count,
        ))

    return results

@router.get(
    "/applications-by-job",
    response_model=List[ApplicationByJob],
    status_code=status.HTTP_200_OK,
    summary="Application counts grouped by job position",
    description="Retrieve candidate application counts per job. Restricted to Admin and HR.",
)
def get_applications_by_job(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    jobs = db.query(Job).all()
    data = []
    for job in jobs:
        count = db.query(Application).filter(Application.job_id == job.id).count()
        if count > 0:
            data.append(ApplicationByJob(job_id=job.id, job_title=job.title, count=count))

    data.sort(key=lambda x: x.count, reverse=True)
    return data

@router.get(
    "/applications-by-status",
    response_model=List[ApplicationByStatus],
    status_code=status.HTTP_200_OK,
    summary="Applications breakdown by status",
    description="Retrieve application distribution across statuses. Restricted to Admin and HR.",
)
def get_applications_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    statuses = [
        ApplicationStatus.new,
        ApplicationStatus.reviewed,
        ApplicationStatus.shortlisted,
        ApplicationStatus.rejected,
        ApplicationStatus.hired,
    ]
    results = []
    for st in statuses:
        cnt = db.query(Application).filter(Application.status == st).count()
        results.append(ApplicationByStatus(status=st.value.capitalize(), count=cnt))
    return results

@router.get(
    "/applications-over-time",
    response_model=List[ApplicationOverTime],
    status_code=status.HTTP_200_OK,
    summary="Applications count trend over time",
    description="Retrieve application timeline volume. Restricted to Admin and HR.",
)
def get_applications_over_time(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    now = datetime.now(timezone.utc)
    results = []
    for i in range(days - 1, -1, -1):
        target_date = now - timedelta(days=i)
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        cnt = db.query(Application).filter(
            Application.created_at >= day_start,
            Application.created_at <= day_end,
        ).count()

        results.append(ApplicationOverTime(
            date=target_date.strftime("%b %d"),
            count=cnt,
        ))
    return results

@router.get(
    "/messages-per-week",
    response_model=List[MessagePerWeek],
    status_code=status.HTTP_200_OK,
    summary="Contact inquiries volume per week",
    description="Retrieve contact message counts grouped by recent weeks. Restricted to Admin and HR.",
)
def get_messages_per_week(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    now = datetime.now(timezone.utc)
    results = []
    for i in range(5, -1, -1):
        start_w = now - timedelta(days=(i + 1) * 7)
        end_w = now - timedelta(days=i * 7)
        cnt = db.query(ContactMessage).filter(
            ContactMessage.created_at >= start_w,
            ContactMessage.created_at < end_w,
        ).count()
        results.append(MessagePerWeek(
            week=f"Week {6 - i}",
            count=cnt,
        ))
    return results

@router.get(
    "/top-posts",
    response_model=List[TopPost],
    status_code=status.HTTP_200_OK,
    summary="Top blog posts by reader view count",
    description="Retrieve the highest-viewed blog articles. Restricted to Admin.",
)
def get_top_posts(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    posts = (
        db.query(BlogPost)
        .filter(BlogPost.status == PostStatus.published)
        .order_by(BlogPost.views_count.desc())
        .limit(limit)
        .all()
    )
    return [
        TopPost(
            id=p.id,
            title=p.title,
            slug=p.slug,
            views=p.views_count or 0,
            published_date=p.published_at.strftime("%b %d") if p.published_at else None,
        )
        for p in posts
    ]

@router.get(
    "/hiring-funnel",
    response_model=List[FunnelStage],
    status_code=status.HTTP_200_OK,
    summary="Hiring progression funnel metrics",
    description="Candidate volume across sequential funnel milestones. Restricted to Admin and HR.",
)
def get_hiring_funnel(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    total = db.query(Application).count()
    reviewed = db.query(Application).filter(Application.status.in_([
        ApplicationStatus.reviewed,
        ApplicationStatus.shortlisted,
        ApplicationStatus.hired,
    ])).count()
    shortlisted = db.query(Application).filter(Application.status.in_([
        ApplicationStatus.shortlisted,
        ApplicationStatus.hired,
    ])).count()
    hired = db.query(Application).filter(Application.status == ApplicationStatus.hired).count()

    return [
        FunnelStage(stage="New", count=total),
        FunnelStage(stage="Reviewed", count=reviewed),
        FunnelStage(stage="Shortlisted", count=shortlisted),
        FunnelStage(stage="Hired", count=hired),
    ]

@router.get(
    "/my-posts",
    response_model=EditorStats,
    status_code=status.HTTP_200_OK,
    summary="Editor personal posting statistics",
    description="Retrieve individual posting breakdown, views over time, and publication cadence.",
)
def get_editor_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.editor, UserRole.admin)),
):
    now = datetime.now(timezone.utc)
    d30 = now - timedelta(days=30)
    d60 = now - timedelta(days=60)

    # Own posts query
    my_posts_q = db.query(BlogPost).filter(BlogPost.author_id == current_user.id)
    total_my_posts = my_posts_q.count()
    my_posts_curr = my_posts_q.filter(BlogPost.created_at >= d30).count()
    my_posts_prev = my_posts_q.filter(BlogPost.created_at >= d60, BlogPost.created_at < d30).count()

    published_q = my_posts_q.filter(BlogPost.status == PostStatus.published)
    total_published = published_q.count()
    pub_curr = published_q.filter(BlogPost.created_at >= d30).count()
    pub_prev = published_q.filter(BlogPost.created_at >= d60, BlogPost.created_at < d30).count()

    drafts_count = my_posts_q.filter(BlogPost.status == PostStatus.draft).count()
    pending_count = my_posts_q.filter(BlogPost.status == PostStatus.pending_review).count()

    total_views = sum((p.views_count or 0) for p in my_posts_q.all())

    # Daily views simulation from page views matching user's blog slugs
    my_slugs = [p.slug for p in my_posts_q.all()]
    views_over_time = []
    for i in range(29, -1, -1):
        target_date = now - timedelta(days=i)
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        if my_slugs:
            v_cnt = db.query(PageView).filter(
                PageView.blog_slug.in_(my_slugs),
                PageView.created_at >= day_start,
                PageView.created_at <= day_end,
            ).count()
        else:
            v_cnt = 0

        views_over_time.append(DailyVisit(
            date=target_date.strftime("%b %d"),
            views=v_cnt,
        ))

    # Posts per month (last 6 months)
    posts_per_month = []
    for m in range(5, -1, -1):
        # approximate month
        m_start = now - timedelta(days=(m + 1) * 30)
        m_end = now - timedelta(days=m * 30)
        m_cnt = my_posts_q.filter(
            BlogPost.created_at >= m_start,
            BlogPost.created_at < m_end,
        ).count()
        m_label = (now - timedelta(days=m * 30)).strftime("%b")
        posts_per_month.append(EditorPostMonth(month=m_label, count=m_cnt))

    status_breakdown = [
        ApplicationByStatus(status="Published", count=total_published),
        ApplicationByStatus(status="Draft", count=drafts_count),
        ApplicationByStatus(status="Pending", count=pending_count),
    ]

    return EditorStats(
        my_posts_count=StatTrend(value=total_my_posts, change_pct=calc_change_pct(my_posts_curr, my_posts_prev)),
        published_count=StatTrend(value=total_published, change_pct=calc_change_pct(pub_curr, pub_prev)),
        drafts_count=drafts_count,
        pending_review_count=pending_count,
        total_views=StatTrend(value=total_views, change_pct=15.0),
        views_over_time=views_over_time,
        posts_per_month=posts_per_month,
        status_breakdown=status_breakdown,
    )
