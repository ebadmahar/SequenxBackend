from datetime import datetime, timezone
import threading
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.blog import BlogPost, PostStatus
from app.models.user import User, UserRole
from app.schemas.blog import BlogCreate, BlogUpdate
from app.utils.slugify import generate_unique_slug
from app.services.email_service import send_newsletter_broadcast_task

def _async_broadcast_newsletter(post_id: int):
    threading.Thread(target=send_newsletter_broadcast_task, args=(post_id,), daemon=True).start()

def create_blog_post(
    db: Session,
    post_in: BlogCreate,
    current_user: User,
) -> BlogPost:
    """Create a new blog post. Editors and admins can directly save as draft or publish."""
    requested_status = post_in.status or PostStatus.draft

    unique_slug = generate_unique_slug(db, BlogPost, post_in.title)
    published_at = datetime.now(timezone.utc) if requested_status == PostStatus.published else None

    blog_post = BlogPost(
        title=post_in.title,
        slug=unique_slug,
        excerpt=post_in.excerpt,
        content=post_in.content,
        cover_image=post_in.cover_image,
        category=post_in.category or "Software Development",
        tags=post_in.tags or "",
        read_time=post_in.read_time or "5 min read",
        featured=bool(post_in.featured),
        author_id=current_user.id,
        author_name=post_in.author_name or current_user.name,
        author_role=post_in.author_role,
        author_avatar=post_in.author_avatar,
        author_bio=post_in.author_bio,
        status=requested_status,
        published_at=published_at,
    )
    if blog_post.featured:
        db.query(BlogPost).update({"featured": False})
    db.add(blog_post)
    db.commit()
    db.refresh(blog_post)
    if requested_status == PostStatus.published:
        _async_broadcast_newsletter(blog_post.id)
    return blog_post

def update_blog_post(
    db: Session,
    post_id: int,
    post_in: BlogUpdate,
    current_user: User,
) -> BlogPost:
    """Update an existing blog post adhering to ownership and role publishing rules."""
    blog_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not blog_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found",
        )

    if current_user.role == UserRole.editor:
        if blog_post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Editors can only modify their own posts",
            )

    update_data = post_in.model_dump(exclude_unset=True)

    if "title" in update_data and update_data["title"] != blog_post.title:
        blog_post.slug = generate_unique_slug(db, BlogPost, update_data["title"], current_id=blog_post.id)

    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == PostStatus.published and blog_post.status != PostStatus.published:
            blog_post.published_at = datetime.now(timezone.utc)
        elif new_status != PostStatus.published:
            blog_post.published_at = None

    prev_status = blog_post.status
    for field, val in update_data.items():
        setattr(blog_post, field, val)

    if blog_post.featured:
        db.query(BlogPost).filter(BlogPost.id != blog_post.id).update({"featured": False})

    db.commit()
    db.refresh(blog_post)
    if "status" in update_data and update_data["status"] == PostStatus.published and prev_status != PostStatus.published:
        _async_broadcast_newsletter(blog_post.id)
    return blog_post

def publish_blog_post(
    db: Session,
    post_id: int,
    current_user: User,
) -> BlogPost:
    """Publish a blog post (available to admin and editor)."""
    blog_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not blog_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found",
        )

    if current_user.role == UserRole.editor and blog_post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editors can only publish their own posts",
        )

    blog_post.status = PostStatus.published
    blog_post.published_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(blog_post)
    _async_broadcast_newsletter(blog_post.id)
    return blog_post

def delete_blog_post(
    db: Session,
    post_id: int,
    current_user: User,
) -> None:
    """Delete a blog post with ownership validation for editors."""
    blog_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not blog_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found",
        )

    if current_user.role == UserRole.editor and blog_post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editors can only delete their own posts",
        )

    db.delete(blog_post)
    db.commit()

