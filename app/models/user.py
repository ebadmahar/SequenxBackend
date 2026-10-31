import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    hr = "hr"
    editor = "editor"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, native_enum=False),
        default=UserRole.editor,
        nullable=False,
    )
    avatar = Column(String(500), nullable=True)
    role_title = Column(String(150), nullable=True)
    bio = Column(String(1000), nullable=True)
    must_change_password = Column(Boolean, default=False, nullable=False)
    session_token = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    blog_posts = relationship("BlogPost", back_populates="author", cascade="all, delete-orphan")
    created_jobs = relationship("Job", back_populates="creator")

