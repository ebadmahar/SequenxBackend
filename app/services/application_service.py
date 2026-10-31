from datetime import datetime, timezone
from typing import Optional
from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.job import Job, JobStatus
from app.schemas.application import ApplicationOut
from app.services.email_service import send_application_emails_task
from app.services.file_service import save_cv_file

async def process_job_application(
    db: Session,
    background_tasks: BackgroundTasks,
    job_id: int,
    full_name: str,
    email: str,
    phone: Optional[str],
    cover_note: Optional[str],
    cv_file: UploadFile,
    website: Optional[str] = None,
) -> ApplicationOut:
    """Validate, record, and dispatch notifications for a candidate job application."""
    # Honeypot spam check
    if website and website.strip():
        return ApplicationOut(
            id=0,
            job_id=job_id,
            full_name=full_name,
            email=email,
            phone=phone,
            cover_note=cover_note,
            cv_path="uploads/cvs/private",
            status=ApplicationStatus.new,
            created_at=datetime.now(timezone.utc),
            job_title="Position",
        )

    # Validate target job
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job position not found",
        )

    if job.status != JobStatus.open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This job position is closed and no longer accepting applications",
        )

    if job.deadline:
        deadline_cmp = job.deadline
        if deadline_cmp.tzinfo is None:
            deadline_cmp = deadline_cmp.replace(tzinfo=timezone.utc)
        if deadline_cmp < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The application deadline for this position has passed",
            )

    # Secure file upload
    stored_cv_path = await save_cv_file(cv_file)

    # Persist record
    application = Application(
        job_id=job.id,
        full_name=full_name.strip(),
        email=email.strip().lower(),
        phone=phone.strip() if phone else None,
        cover_note=cover_note.strip() if cover_note else None,
        cv_path=stored_cv_path,
        status=ApplicationStatus.new,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    # Trigger async email notifications
    background_tasks.add_task(send_application_emails_task, application.id)

    return ApplicationOut(
        id=application.id,
        job_id=application.job_id,
        full_name=application.full_name,
        email=application.email,
        phone=application.phone,
        cover_note=application.cover_note,
        cv_path=application.cv_path,
        status=application.status,
        created_at=application.created_at,
        job_title=job.title,
    )

