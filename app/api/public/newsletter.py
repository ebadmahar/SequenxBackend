from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.newsletter import NewsletterSubscriber
from app.schemas.newsletter import NewsletterSubscribeIn
from app.services.email_service import send_smtp_email

router = APIRouter(prefix="/newsletter", tags=["Newsletter Public"])

@router.post(
    "/subscribe",
    status_code=status.HTTP_200_OK,
    summary="Subscribe to SeQuenX Journal Newsletter",
    description="Subscribe an email address to receive new articles, engineering insights, and tech updates.",
)
def subscribe_newsletter(
    payload: NewsletterSubscribeIn,
    db: Session = Depends(get_db),
):
    clean_email = payload.email.strip().lower()

    existing = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == clean_email).first()
    if existing:
        if not existing.is_active:
            existing.is_active = True
            db.commit()
            return {"message": "Welcome back! Your newsletter subscription has been reactivated."}
        return {"message": "You are already subscribed to the SeQuenX Journal."}

    subscriber = NewsletterSubscriber(email=clean_email, is_active=True)
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)

    # Optional welcome email
    welcome_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; color: #1e293b; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;">
      <div style="text-align: center; margin-bottom: 24px;">
        <h2 style="color: #0B1F42; margin: 0; font-size: 22px;">Welcome to SeQuenX Journal</h2>
        <p style="color: #64748b; font-size: 13px; margin-top: 6px;">Technology, Engineering &amp; Strategic Delivery Insights</p>
      </div>
      <p style="font-size: 14px; line-height: 1.6;">Thank you for subscribing! You will receive our latest articles, case studies, and engineering updates directly in your inbox whenever a new post is published.</p>
      <div style="margin: 28px 0; text-align: center;">
        <a href="http://localhost:3000/blog" style="background: #1a56db; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-size: 13px; font-weight: bold; display: inline-block;">
          Browse All Articles
        </a>
      </div>
      <p style="font-size: 11px; color: #94a3b8; text-align: center; border-top: 1px solid #f1f5f9; padding-top: 16px;">
        SeQuenX &bull; Dedicated Remote Engineering Teams &amp; Digital Solutions
      </p>
    </div>
    """
    try:
        send_smtp_email(
            to_email=clean_email,
            subject="Welcome to SeQuenX Journal!",
            html_content=welcome_html,
        )
    except Exception:
        pass

    return {"message": "Thank you for subscribing to SeQuenX Journal!"}

