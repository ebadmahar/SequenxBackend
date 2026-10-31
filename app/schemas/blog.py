from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.models.blog import PostStatus

class BlogBase(BaseModel):
    title: str
    excerpt: Optional[str] = None
    content: str
    cover_image: Optional[str] = None
    category: Optional[str] = "Software Development"
    tags: Optional[str] = ""
    read_time: Optional[str] = "5 min read"
    featured: Optional[bool] = False
    author_name: Optional[str] = None
    author_role: Optional[str] = None
    author_avatar: Optional[str] = None
    author_bio: Optional[str] = None

class BlogCreate(BlogBase):
    status: Optional[PostStatus] = PostStatus.draft

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Getting Started with Modern Web Development",
                "excerpt": "A brief overview of modern web engineering principles and tooling.",
                "content": "# Modern Web Development\n\nFull article contents go here...",
                "cover_image": "/static/blog_images/hero.webp",
                "category": "Software Development",
                "tags": "Next.js, React, Web",
                "read_time": "8 min read",
                "featured": True,
                "author_name": "Ali Raza",
                "author_role": "Senior Engineering Manager",
                "author_avatar": "/images/blog/author-ali.jpg",
                "author_bio": "Ali leads engineering teams with a focus on scalable software solutions.",
                "status": "draft",
            }
        }
    )

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    read_time: Optional[str] = None
    featured: Optional[bool] = None
    author_name: Optional[str] = None
    author_role: Optional[str] = None
    author_avatar: Optional[str] = None
    author_bio: Optional[str] = None
    status: Optional[PostStatus] = None

class BlogOut(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    cover_image: Optional[str] = None
    category: Optional[str] = "Software Development"
    tags: Optional[str] = ""
    read_time: Optional[str] = "5 min read"
    featured: bool = False
    status: PostStatus
    views_count: int = 0
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    author_role: Optional[str] = None
    author_avatar: Optional[str] = None
    author_bio: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class BlogListResponse(BaseModel):
    items: List[BlogOut]
    total: int
    page: int
    limit: int
    pages: int
