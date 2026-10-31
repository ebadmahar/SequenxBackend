from math import ceil
from pathlib import Path
from typing import Optional
import io
import zipfile
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.application import Application, ApplicationStatus
from app.models.user import User, UserRole
from app.schemas.application import (
    ApplicationListResponse,
    ApplicationOut,
    ApplicationStatusUpdate,
)
from app.services.file_service import resolve_safe_cv_path

router = APIRouter(prefix="/admin/applications", tags=["Admin Applications"])

@router.get(
    "/counts",
    status_code=status.HTTP_200_OK,
    summary="Get application status counts",
    description="Retrieve count of candidate applications broken down by workflow status.",
)
def get_application_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    new_count = db.query(Application).filter(Application.status == ApplicationStatus.new).count()
    reviewed_count = db.query(Application).filter(Application.status == ApplicationStatus.reviewed).count()
    shortlisted_count = db.query(Application).filter(Application.status == ApplicationStatus.shortlisted).count()
    rejected_count = db.query(Application).filter(Application.status == ApplicationStatus.rejected).count()
    hired_count = db.query(Application).filter(Application.status == ApplicationStatus.hired).count()
    total_count = db.query(Application).count()
    return {
        "new_count": new_count,
        "reviewed_count": reviewed_count,
        "shortlisted_count": shortlisted_count,
        "rejected_count": rejected_count,
        "hired_count": hired_count,
        "total_count": total_count,
    }

@router.get(
    "/bulk-download",
    status_code=status.HTTP_200_OK,
    summary="Download candidate CVs as a ZIP archive",
    description="Bulk download candidate resumes. Pass comma-separated IDs via 'ids' or omit to download all.",
)
def bulk_download_cvs(
    ids: Optional[str] = Query(None, description="Comma-separated application IDs, e.g. 1,2,3. If omitted, downloads all CVs."),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    query = db.query(Application)
    if ids and ids.strip():
        parsed_ids = [int(i.strip()) for i in ids.split(",") if i.strip().isdigit()]
        if parsed_ids:
            query = query.filter(Application.id.in_(parsed_ids))

    applications = query.all()
    if not applications:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching candidate CV records found to download",
        )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        added_count = 0
        for app in applications:
            try:
                file_path = resolve_safe_cv_path(app.cv_path)
                if file_path.exists() and file_path.is_file():
                    safe_name = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in app.full_name).strip().replace(" ", "_")
                    archive_name = f"CV_{safe_name}_{app.id}{file_path.suffix}"
                    zf.write(file_path, arcname=archive_name)
                    added_count += 1
            except Exception:
                continue

    if added_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No candidate CV files could be located on disk",
        )

    zip_buffer.seek(0)
    filename = "Candidate_CVs_Selected.zip" if (ids and ids.strip()) else "Candidate_CVs_All.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@router.get(
    "",
    response_model=ApplicationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List job applications",
    description="Retrieve candidacies with filtering by job ID, status, and pagination.",
)
def list_applications(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    job_id: Optional[int] = Query(None, description="Filter by specific job opening ID"),
    status_filter: Optional[ApplicationStatus] = Query(None, alias="status", description="Filter by application status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    query = db.query(Application)

    if job_id is not None:
        query = query.filter(Application.job_id == job_id)
    if status_filter is not None:
        query = query.filter(Application.status == status_filter)

    total = query.count()
    pages = ceil(total / limit) if total > 0 else 0
    offset = (page - 1) * limit

    records = query.order_by(Application.created_at.desc()).offset(offset).limit(limit).all()

    items = []
    for app in records:
        out = ApplicationOut.model_validate(app)
        if app.job:
            out.job_title = app.job.title
        items.append(out)

    return ApplicationListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )

@router.get(
    "/{id}",
    response_model=ApplicationOut,
    status_code=status.HTTP_200_OK,
    summary="Get job application details",
    description="Retrieve full details for a specific candidacy submission.",
)
def get_application(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    app = db.query(Application).filter(Application.id == id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application record not found",
        )
    out = ApplicationOut.model_validate(app)
    if app.job:
        out.job_title = app.job.title
    return out

@router.patch(
    "/{id}/status",
    response_model=ApplicationOut,
    status_code=status.HTTP_200_OK,
    summary="Update application status",
    description="Update review workflow status (new, reviewed, shortlisted, rejected).",
)
def update_application_status(
    id: int,
    status_in: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    app = db.query(Application).filter(Application.id == id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application record not found",
        )

    app.status = status_in.status
    db.commit()
    db.refresh(app)

    out = ApplicationOut.model_validate(app)
    if app.job:
        out.job_title = app.job.title
    return out

@router.get(
    "/{id}/cv",
    status_code=status.HTTP_200_OK,
    summary="Download candidate CV document",
    description="Securely download the private CV document associated with an application.",
)
def download_application_cv(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.hr)),
):
    app = db.query(Application).filter(Application.id == id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application record not found",
        )

    file_path = resolve_safe_cv_path(app.cv_path)
    extension = file_path.suffix
    download_filename = f"CV_{app.full_name.replace(' ', '_')}_{app.id}{extension}"

    return FileResponse(
        path=str(file_path),
        filename=download_filename,
        media_type="application/octet-stream",
    )

