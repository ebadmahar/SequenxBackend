from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class PageViewCreate(BaseModel):
    path: str
    blog_slug: Optional[str] = None
    referrer: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "path": "/blog/future-of-ai-in-pakistan",
                "blog_slug": "future-of-ai-in-pakistan",
                "referrer": "https://google.com",
            }
        }
    )

class StatTrend(BaseModel):
    value: int
    change_pct: float

class OverviewStats(BaseModel):
    total_visitors: StatTrend
    published_posts: StatTrend
    draft_posts: int
    pending_posts: int
    open_jobs: StatTrend
    closed_jobs: int
    new_applications: StatTrend
    total_applications: int
    shortlisted_applications: StatTrend
    unread_messages: StatTrend
    total_messages: int
    active_users: StatTrend

class DailyVisit(BaseModel):
    date: str
    views: int

class ApplicationByJob(BaseModel):
    job_id: int
    job_title: str
    count: int

class ApplicationByStatus(BaseModel):
    status: str
    count: int

class ApplicationOverTime(BaseModel):
    date: str
    count: int

class MessagePerWeek(BaseModel):
    week: str
    count: int

class TopPost(BaseModel):
    id: int
    title: str
    slug: str
    views: int
    published_date: Optional[str] = None

class FunnelStage(BaseModel):
    stage: str
    count: int

class EditorPostMonth(BaseModel):
    month: str
    count: int

class EditorStats(BaseModel):
    my_posts_count: StatTrend
    published_count: StatTrend
    drafts_count: int
    pending_review_count: int
    total_views: StatTrend
    views_over_time: List[DailyVisit]
    posts_per_month: List[EditorPostMonth]
    status_breakdown: List[ApplicationByStatus]
