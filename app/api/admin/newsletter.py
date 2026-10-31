from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.newsletter import NewsletterSubscriber
from app.models.user import User, UserRole
from app.schemas.newsletter import NewsletterSubscriberOut, NewsletterSubscribersListResponse

router = APIRouter(prefix="/admin/newsletter", tags=["Admin Newsletter"])

@router.get(
    "/subscribers",
    response_model=NewsletterSubscribersListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all newsletter subscribers",
    description="Retrieve all newsletter subscribers with optional search filter.",
)
def list_subscribers(
    search: Optional[str] = Query(None, description="Search by email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.editor)),
):
    query = db.query(NewsletterSubscriber)
    if search:
        query = query.filter(NewsletterSubscriber.email.ilike(f"%{search.strip()}%"))

    total = query.count()
    subscribers = query.order_by(NewsletterSubscriber.created_at.desc()).all()

    return NewsletterSubscribersListResponse(
        items=[NewsletterSubscriberOut.model_validate(s) for s in subscribers],
        total=total,
    )

@router.delete(
    "/subscribers/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete subscriber",
    description="Remove a subscriber from the newsletter database.",
)
def delete_subscriber(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    sub = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.id == id).first()
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found",
        )
    db.delete(sub)
    db.commit()
    return None

