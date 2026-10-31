import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class JobType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    internship = "internship"

class JobStatus(str, enum.Enum):
    open = "open"
    closed = "closed"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    department = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    job_type = Column(
        Enum(JobType, native_enum=False),
        default=JobType.full_time,
        nullable=False,
    )
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    status = Column(
        Enum(JobStatus, native_enum=False),
        default=JobStatus.open,
        nullable=False,
    )
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    creator = relationship("User", back_populates="created_jobs")
    applications = relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan",
    )

