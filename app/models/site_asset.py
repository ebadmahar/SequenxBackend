from sqlalchemy import Column, DateTime, Integer, String, func
from app.db.session import Base

class SiteAsset(Base):
    __tablename__ = "site_assets"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    page = Column(String(50), index=True, nullable=False)  # "global", "homepage", "about", "services", "team", "careers", "contact", "tech"
    location_keyword = Column(String(150), nullable=False) # e.g. "Homepage Top Hero Background"
    asset_type = Column(String(30), nullable=False)        # "image", "icon", "logo", "background"
    aspect_ratio = Column(String(30), nullable=False)      # "16:9", "1:1", "4:3", "21:9", "Auto"
    dimensions = Column(String(40), nullable=False)        # e.g. "1920 × 1080 px", "64 × 64 px"
    current_url = Column(String(500), nullable=True)       # Custom uploaded file URL (None = using fallback)
    fallback_url = Column(String(500), nullable=False)     # Default static path in /public
    alt_text = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    updated_by = Column(String(100), nullable=True)

