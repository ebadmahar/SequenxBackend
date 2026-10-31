from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.job import Job
from app.models.user import User, UserRole
from app.schemas.job import JobCreate, JobOut, JobStatusUpdate, JobUpdate

router = APIRouter(prefix="/admin/jobs", tags=["Admin Jobs"])

@router.get(
    "",
    response_model=List[JobOut],
    status_code=status.HTTP_200_OK,
    summary="List all job openings",
    description="Retrieve all job positions (both open and closed). Accessible to Admin and HR.",
)
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    return db.query(Job).order_by(Job.created_at.desc()).all()

@router.post(
    "",
    response_model=JobOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job opening",
    description="Publish a new career opportunity vacancy.",
)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    job = Job(
        title=job_in.title.strip(),
        department=job_in.department.strip() if job_in.department else None,
        location=job_in.location.strip() if job_in.location else None,
        job_type=job_in.job_type,
        description=job_in.description.strip(),
        requirements=job_in.requirements.strip() if job_in.requirements else None,
        deadline=job_in.deadline,
        status=job_in.status,
        created_by=current_user.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get(
    "/{id}",
    response_model=JobOut,
    status_code=status.HTTP_200_OK,
    summary="Get job opening details by ID",
    description="Retrieve details for a specific job vacancy.",
)
def get_job_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job position not found",
        )
    return job

@router.put(
    "/{id}",
    response_model=JobOut,
    status_code=status.HTTP_200_OK,
    summary="Update job opening",
    description="Modify parameters or descriptions of an existing career opportunity.",
)
def update_job(
    id: int,
    job_in: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job position not found",
        )

    update_data = job_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(job, field, val)

    db.commit()
    db.refresh(job)
    return job

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete job opening",
    description="Permanently remove a job vacancy and all associated applications.",
)
def delete_job(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job position not found",
        )
    db.delete(job)
    db.commit()
    return None

@router.patch(
    "/{id}/status",
    response_model=JobOut,
    status_code=status.HTTP_200_OK,
    summary="Update job status",
    description="Open or close a job opening for applications.",
)
def update_job_status(
    id: int,
    status_in: JobStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job position not found",
        )

    job.status = status_in.status
    db.commit()
    db.refresh(job)
    return job

