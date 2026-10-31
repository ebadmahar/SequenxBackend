from math import ceil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.contact import ContactMessage
from app.models.user import User, UserRole
from app.schemas.contact import ContactListResponse, ContactMarkRead, ContactOut

router = APIRouter(prefix="/admin/messages", tags=["Admin Messages"])

@router.get(
    "",
    response_model=ContactListResponse,
    status_code=status.HTTP_200_OK,
    summary="List contact inquiries",
    description="Retrieve incoming contact messages with filtering by read status and pagination.",
)
def list_messages(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    query = db.query(ContactMessage)
    if is_read is not None:
        query = query.filter(ContactMessage.is_read == is_read)

    total = query.count()
    pages = ceil(total / limit) if total > 0 else 0
    offset = (page - 1) * limit

    records = query.order_by(ContactMessage.created_at.desc()).offset(offset).limit(limit).all()

    return ContactListResponse(
        items=records,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )

@router.get(
    "/{id}",
    response_model=ContactOut,
    status_code=status.HTTP_200_OK,
    summary="Get contact message by ID",
    description="Retrieve details and content of a specific contact message.",
)
def get_message(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    message = db.query(ContactMessage).filter(ContactMessage.id == id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact message not found",
        )
    return message

@router.patch(
    "/{id}/read",
    response_model=ContactOut,
    status_code=status.HTTP_200_OK,
    summary="Update message read status",
    description="Mark a message as read or unread.",
)
def mark_message_read_status(
    id: int,
    payload: ContactMarkRead,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    message = db.query(ContactMessage).filter(ContactMessage.id == id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact message not found",
        )

    message.is_read = payload.is_read
    db.commit()
    db.refresh(message)
    return message

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contact message",
    description="Permanently remove a contact inquiry.",
)
def delete_message(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    message = db.query(ContactMessage).filter(ContactMessage.id == id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact message not found",
        )
    db.delete(message)
    db.commit()
    return None

