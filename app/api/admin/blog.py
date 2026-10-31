from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.blog import BlogPost, PostStatus
from app.models.user import User, UserRole
from app.schemas.blog import BlogCreate, BlogListResponse, BlogOut, BlogUpdate
from app.services.blog_service import (
    create_blog_post,
    delete_blog_post,
    publish_blog_post,
    update_blog_post,
)
from app.services.file_service import save_blog_image

router = APIRouter(prefix="/admin/blog", tags=["Admin Blog"])

@router.get(
    "",
    response_model=BlogListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all blog posts",
    description="Retrieve all blog articles (drafts, pending review, published) with pagination.",
)
def list_admin_blogs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status_filter: Optional[PostStatus] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.editor)),
):
    query = db.query(BlogPost)
    if status_filter:
        query = query.filter(BlogPost.status == status_filter)

    total = query.count()
    pages = ceil(total / limit) if total > 0 else 0
    offset = (page - 1) * limit

    posts = query.order_by(BlogPost.created_at.desc()).offset(offset).limit(limit).all()

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

@router.post(
    "",
    response_model=BlogOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new blog post",
    description="Create a new blog article. Editors can save as draft or pending_review; only admins can publish directly.",
)
def create_blog(
    post_in: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.editor)),
):
    post = create_blog_post(db, post_in, current_user)
    post_data = BlogOut.model_validate(post)
    post_data.author_name = current_user.name
    return post_data

@router.get(
    "/{id}",
    response_model=BlogOut,
    status_code=status.HTTP_200_OK,
    summary="Get blog post by ID",
    description="Retrieve details of a specific blog post by ID.",
)
def get_blog_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.editor)),
):
    post = db.query(BlogPost).filter(BlogPost.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found",
        )
    post_data = BlogOut.model_validate(post)
    if not post_data.author_name and post.author:
        post_data.author_name = post.author.name
    return post_data

@router.put(
    "/{id}",
    response_model=BlogOut,
    status_code=status.HTTP_200_OK,
    summary="Update blog post",
    description="Update a blog post. Editors can only edit their own posts and cannot publish.",
)
def update_blog(
    id: int,
    post_in: BlogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.editor)),
):
    post = update_blog_post(db, id, post_in, current_user)
    post_data = BlogOut.model_validate(post)
    if not post_data.author_name and post.author:
        post_data.author_name = post.author.name
    return post_data

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete blog post",
    description="Delete a blog post. Editors can only delete their own articles.",
)
def delete_blog(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.editor)),
):
    delete_blog_post(db, id, current_user)
    return None

@router.post(
    "/{id}/publish",
    response_model=BlogOut,
    status_code=status.HTTP_200_OK,
    summary="Publish a blog post",
    description="Publish a blog article. Accessible by administrators and editors.",
)
def publish_blog(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.editor)),
):
    post = publish_blog_post(db, id, current_user)
    post_data = BlogOut.model_validate(post)
    if not post_data.author_name and post.author:
        post_data.author_name = post.author.name
    return post_data

@router.post(
    "/upload-image",
    status_code=status.HTTP_201_CREATED,
    summary="Upload blog image",
    description="Upload an image (JPG, PNG, WEBP, max 3MB) for use in blog covers or content.",
)
async def upload_blog_image(
    file: UploadFile = File(..., description="Image file (JPG, PNG, WEBP, max 3MB)"),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.editor)),
):
    image_url = await save_blog_image(file)
    return {"url": image_url}

