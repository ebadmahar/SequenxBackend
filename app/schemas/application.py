from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.application import ApplicationStatus

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "shortlisted",
            }
        }
    )

class ApplicationOut(BaseModel):
    id: int
    job_id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    cover_note: Optional[str] = None
    cv_path: str
    status: ApplicationStatus
    created_at: datetime
    job_title: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "job_id": 2,
                "job_title": "Senior Backend Engineer",
                "full_name": "Alice Wonderland",
                "email": "alice@example.com",
                "phone": "+1-555-0199",
                "cover_note": "Excited to apply for this backend opportunity...",
                "cv_path": "uploads/cvs/a1b2c3d4-e5f6-7890-1234-56789abcdef0.pdf",
                "status": "new",
                "created_at": "2026-10-29T14:30:00Z",
            }
        },
    )

class ApplicationListResponse(BaseModel):
    items: List[ApplicationOut]
    total: int
    page: int
    limit: int
    pages: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 12,
                "page": 1,
                "limit": 10,
                "pages": 2,
            }
        }
    )

