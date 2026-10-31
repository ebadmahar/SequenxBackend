from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.blog import BlogPost
from app.models.pageview import PageView
from app.schemas.analytics import PageViewCreate
from app.utils.rate_limit import limiter

router = APIRouter(prefix="/analytics", tags=["Public Analytics"])

@router.post(
    "/pageview",
    status_code=status.HTTP_201_CREATED,
    summary="Record a page view",
    description="Track page hits and blog post view counters from the public website.",
)
@limiter.limit("60/minute")
def record_page_view(
    request: Request,
    payload: PageViewCreate,
    db: Session = Depends(get_db),
):
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    page_view = PageView(
        path=payload.path.strip()[:500],
        blog_slug=payload.blog_slug.strip()[:255] if payload.blog_slug else None,
        referrer=payload.referrer.strip()[:500] if payload.referrer else None,
        user_agent=user_agent[:500] if user_agent else None,
        ip_address=ip_addr,
    )
    db.add(page_view)

    if payload.blog_slug:
        blog = db.query(BlogPost).filter(BlogPost.slug == payload.blog_slug.strip()).first()
        if blog:
            blog.views_count = (blog.views_count or 0) + 1

    db.commit()
    return {"status": "recorded"}
