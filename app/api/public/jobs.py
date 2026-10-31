from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.job import Job, JobStatus
from app.schemas.application import ApplicationOut
from app.schemas.job import JobOut
from app.services.application_service import process_job_application
from app.utils.rate_limit import limiter

router = APIRouter(prefix="/jobs", tags=["Public Careers"])

@router.get(
    "",
    response_model=List[JobOut],
    status_code=status.HTTP_200_OK,
    summary="List open job openings",
    description="Retrieve all currently active job opportunities accepting candidates.",
)
def get_open_jobs(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    jobs = db.query(Job).filter(Job.status == JobStatus.open).order_by(Job.created_at.desc()).all()
    active_jobs = []
    for job in jobs:
        if job.deadline:
            dl = job.deadline if job.deadline.tzinfo else job.deadline.replace(tzinfo=timezone.utc)
            if dl < now:
                continue
        active_jobs.append(job)
    return active_jobs

@router.get(
    "/{id}",
    response_model=JobOut,
    status_code=status.HTTP_200_OK,
    summary="Get job opening details",
    description="Retrieve details for a specific active job opening by its ID.",
)
def get_job_detail(
    id: int,
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == id, Job.status == JobStatus.open).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job position not found or no longer active",
        )
    return job

@router.post(
    "/{id}/apply",
    response_model=ApplicationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Apply for a job position",
    description="Submit candidate details and upload a CV document for an open position.",
)
@limiter.limit("5/hour")
async def apply_for_job(
    request: Request,
    id: int,
    background_tasks: BackgroundTasks,
    full_name: str = Form(..., description="Full legal name of candidate"),
    email: str = Form(..., description="Email address of candidate"),
    phone: Optional[str] = Form(None, description="Contact phone number"),
    cover_note: Optional[str] = Form(None, description="Optional introduction note"),
    website: Optional[str] = Form(None, description="Honeypot field; leave blank"),
    cv: UploadFile = File(..., description="CV document in PDF, DOC, or DOCX format (max 5MB)"),
    db: Session = Depends(get_db),
):
    return await process_job_application(
        db=db,
        background_tasks=background_tasks,
        job_id=id,
        full_name=full_name,
        email=email,
        phone=phone,
        cover_note=cover_note,
        cv_file=cv,
        website=website,
    )

