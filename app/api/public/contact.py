from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.contact import ContactMessage
from app.schemas.contact import ContactCreate, ContactOut
from app.services.email_service import send_contact_email_task
from app.utils.rate_limit import limiter

router = APIRouter(prefix="/contact", tags=["Public Contact"])

@router.post(
    "",
    response_model=ContactOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit contact inquiry",
    description="Send a message or inquiry to the organization with automatic notifications to HR.",
)
@limiter.limit("5/hour")
def submit_contact_message(
    request: Request,
    payload: ContactCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Honeypot silent bypass
    if payload.website and payload.website.strip():
        return ContactOut(
            id=0,
            name=payload.name,
            email=payload.email,
            subject=payload.subject,
            message=payload.message,
            is_read=False,
            created_at=datetime.now(timezone.utc),
        )

    contact = ContactMessage(
        name=payload.name.strip(),
        email=payload.email.strip().lower(),
        subject=payload.subject.strip(),
        message=payload.message.strip(),
        is_read=False,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    background_tasks.add_task(send_contact_email_task, contact.id)

    return contact

