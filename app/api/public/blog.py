from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.blog import BlogPost, PostStatus
from app.schemas.blog import BlogListResponse, BlogOut

router = APIRouter(prefix="/blog", tags=["Public Blog"])

@router.get(
    "",
    response_model=BlogListResponse,
    status_code=status.HTTP_200_OK,
    summary="List published blog posts",
    description="Retrieve published blog posts with pagination and optional search filter by title or content.",
)
def get_published_blogs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for title or excerpt"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    query = db.query(BlogPost).filter(BlogPost.status == PostStatus.published)

    if category and category != "All Posts":
        query = query.filter(BlogPost.category == category)

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            or_(
                BlogPost.title.ilike(search_filter),
                BlogPost.excerpt.ilike(search_filter),
                BlogPost.content.ilike(search_filter),
            )
        )

    total = query.count()
    pages = ceil(total / limit) if total > 0 else 0
    offset = (page - 1) * limit

    posts = query.order_by(BlogPost.published_at.desc().nullslast()).offset(offset).limit(limit).all()

    items = []
    for post in posts:
        post_data = BlogOut.model_validate(post)
        if not post_data.author_name and post.author:
            post_data.author_name = post.author.name
        items.append(post_data)

    return BlogListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )

@router.get(
    "/{slug}",
    response_model=BlogOut,
    status_code=status.HTTP_200_OK,
    summary="Get published blog post by slug",
    description="Retrieve a single published blog article using its unique URL-friendly slug and increment view count.",
)
def get_published_blog_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    post = (
        db.query(BlogPost)
        .filter(BlogPost.slug == slug, BlogPost.status == PostStatus.published)
        .first()
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog article not found or has not been published yet",
        )

    # Increment view count
    post.views_count = (post.views_count or 0) + 1
    db.commit()
    db.refresh(post)

    post_data = BlogOut.model_validate(post)
    if not post_data.author_name and post.author:
        post_data.author_name = post.author.name
    return post_data
