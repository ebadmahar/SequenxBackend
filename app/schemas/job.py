from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.models.job import JobStatus, JobType

class JobBase(BaseModel):
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: JobType = JobType.full_time
    description: str
    requirements: Optional[str] = None
    deadline: Optional[datetime] = None

class JobCreate(JobBase):
    status: Optional[JobStatus] = JobStatus.open

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Senior Backend Engineer",
                "department": "Engineering",
                "location": "Remote / New York",
                "job_type": "full_time",
                "description": "We are seeking a senior backend engineer proficient in Python and FastAPI.",
                "requirements": "5+ years backend development, experience with relational databases and Docker.",
                "status": "open",
                "deadline": "2026-12-31T23:59:59Z",
            }
        }
    )

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[JobStatus] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "closed",
            }
        }
    )

class JobStatusUpdate(BaseModel):
    status: JobStatus

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "closed",
            }
        }
    )

class JobOut(BaseModel):
    id: int
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: JobType
    description: str
    requirements: Optional[str] = None
    status: JobStatus
    deadline: Optional[datetime] = None
    created_by: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Senior Backend Engineer",
                "department": "Engineering",
                "location": "Remote / New York",
                "job_type": "full_time",
                "description": "We are looking for an experienced backend developer...",
                "requirements": "Proficiency in FastAPI and SQLAlchemy.",
                "status": "open",
                "deadline": "2026-12-31T23:59:59Z",
                "created_by": 1,
                "created_at": "2026-10-29T10:00:00Z",
            }
        },
    )

class JobListResponse(BaseModel):
    items: List[JobOut]
    total: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 5,
            }
        }
    )

