import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import engine
from app.models.setting import Setting
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """Create database tables and seed initial administrator and settings."""
    # Create tables fallback
    Base.metadata.create_all(bind=engine)

    # Check and seed first admin
    admin = db.query(User).filter(User.email == settings.FIRST_ADMIN_EMAIL).first()
    if not admin:
        logger.info(f"Creating initial administrator: {settings.FIRST_ADMIN_EMAIL}")
        admin = User(
            name=settings.FIRST_ADMIN_NAME,
            email=settings.FIRST_ADMIN_EMAIL,
            password_hash=get_password_hash(settings.FIRST_ADMIN_PASSWORD),
            role=UserRole.admin,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    else:
        logger.info("Administrator user already exists.")

    # Check and seed default HR email setting
    hr_setting = db.query(Setting).filter(Setting.key == "hr_email").first()
    if not hr_setting:
        hr_setting = Setting(
            key="hr_email",
            value=settings.HR_EMAIL,
            description="Recipient email address for job applications and contact notifications",
        )
        db.add(hr_setting)
        db.commit()

if __name__ == "__main__":
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

