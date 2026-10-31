import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class PostStatus(str, enum.Enum):
    draft = "draft"
    pending_review = "pending_review"
    published = "published"

class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    excerpt = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    cover_image = Column(String(500), nullable=True)
    category = Column(String(100), default="Software Development", nullable=True)
    tags = Column(String(255), default="", nullable=True)
    read_time = Column(String(50), default="5 min read", nullable=True)
    featured = Column(Boolean, default=False, nullable=False)
    status = Column(
        Enum(PostStatus, native_enum=False),
        default=PostStatus.draft,
        nullable=False,
    )
    views_count = Column(Integer, default=0, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    author_name = Column(String(150), nullable=True)
    author_role = Column(String(150), nullable=True)
    author_avatar = Column(String(500), nullable=True)
    author_bio = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    author = relationship("User", back_populates="blog_posts")
