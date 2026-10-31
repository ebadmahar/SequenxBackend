import logging
import mimetypes
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.application import Application
from app.models.blog import BlogPost, PostStatus
from app.models.contact import ContactMessage
from app.models.job import Job
from app.models.newsletter import NewsletterSubscriber
from app.models.setting import Setting

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "email"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)

def get_hr_recipient_email(db: Session) -> str:
    """Retrieve HR notification email from settings table or fallback to environment configuration."""
    setting = db.query(Setting).filter(Setting.key == "hr_email").first()
    if setting and setting.value and setting.value.strip():
        return setting.value.strip()
    return settings.HR_EMAIL or ""

def get_smtp_config(db: Optional[Session] = None) -> Dict[str, any]:
    """Retrieve dynamic SMTP settings from database table, falling back to environment config."""
    config = {
        "host": settings.SMTP_HOST or "",
        "port": settings.SMTP_PORT or 587,
        "user": settings.SMTP_USER or "",
        "password": settings.SMTP_PASSWORD or "",
        "from_email": settings.SMTP_FROM_EMAIL or "",
        "from_name": settings.SMTP_FROM_NAME or "SeQuenX",
        "tls": settings.SMTP_TLS,
    }

    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        rows = db.query(Setting).filter(
            Setting.key.in_([
                "smtp_host",
                "smtp_port",
                "smtp_user",
                "smtp_password",
                "smtp_from_email",
                "smtp_from_name",
                "smtp_tls",
            ])
        ).all()
        for row in rows:
            if not row.value:
                continue
            val = row.value.strip()
            if row.key == "smtp_host":
                config["host"] = val
            elif row.key == "smtp_port":
                try:
                    config["port"] = int(val)
                except ValueError:
                    pass
            elif row.key == "smtp_user":
                config["user"] = val
            elif row.key == "smtp_password":
                config["password"] = val
            elif row.key == "smtp_from_email":
                config["from_email"] = val
            elif row.key == "smtp_from_name":
                config["from_name"] = val
            elif row.key == "smtp_tls":
                config["tls"] = val.lower() in ("true", "1", "yes")
    except Exception as exc:
        logger.warning(f"Could not load dynamic SMTP settings from DB: {exc}")
    finally:
        if should_close:
            db.close()

    return config

def send_smtp_email(
    to_email: str,
    subject: str,
    html_content: str,
    attachment_path: Optional[str] = None,
    db: Optional[Session] = None,
) -> None:
    """Send an HTML email via SMTP with optional attachment, catching and logging any errors."""
    if not to_email or not to_email.strip():
        logger.warning(f"[SMTP Skipped] No recipient email specified for subject: '{subject}'")
        return

    smtp_cfg = get_smtp_config(db)
    host = smtp_cfg["host"]

    if not host or host in ("smtp.example.com", "localhost", "none", ""):
        logger.info(
            f"[SMTP Disabled] Host is empty. Simulated dispatch to: {to_email} | Subject: '{subject}'"
        )
        return

    try:
        from_header = f"{smtp_cfg['from_name']} <{smtp_cfg['from_email']}>" if smtp_cfg['from_email'] else "SeQuenX"
        msg = MIMEMultipart()
        msg["From"] = from_header
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_content, "html", "utf-8"))

        if attachment_path and os.path.isfile(attachment_path):
            filename = os.path.basename(attachment_path)
            content_type, _ = mimetypes.guess_type(attachment_path)
            subtype = content_type.split("/")[1] if content_type and "/" in content_type else "octet-stream"

            with open(attachment_path, "rb") as f:
                attachment = MIMEApplication(f.read(), _subtype=subtype)
                attachment.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(attachment)

        with smtplib.SMTP(host, smtp_cfg["port"], timeout=20) as server:
            if smtp_cfg["tls"]:
                server.starttls()
            if smtp_cfg["user"] and smtp_cfg["password"]:
                server.login(smtp_cfg["user"], smtp_cfg["password"])
            server.send_message(msg)

        logger.info(f"Successfully dispatched email to {to_email} with subject '{subject}'.")
    except Exception as exc:
        logger.error(f"Failed to send email to {to_email}: {exc}", exc_info=True)

def send_application_emails_task(application_id: int) -> None:
    """Background task to notify HR of a new application and send receipt confirmation to applicant."""
    db = SessionLocal()
    try:
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            logger.error(f"Application #{application_id} not found for email dispatch.")
            return

        job = db.query(Job).filter(Job.id == application.job_id).first()
        job_title = job.title if job else "Position"

        hr_email = get_hr_recipient_email(db)

        # 1. Email HR with CV attached
        if hr_email:
            hr_template = jinja_env.get_template("new_application.html")
            hr_html = hr_template.render(
                job_title=job_title,
                candidate_name=application.full_name,
                candidate_email=application.email,
                candidate_phone=application.phone or "Not provided",
                cover_note=application.cover_note or "",
                created_at=application.created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if application.created_at else "",
            )

            base_dir = Path(__file__).resolve().parent.parent.parent
            cv_absolute_path = str(base_dir / application.cv_path) if application.cv_path else None

            send_smtp_email(
                to_email=hr_email,
                subject=f"New Application: {job_title} - {application.full_name}",
                html_content=hr_html,
                attachment_path=cv_absolute_path,
                db=db,
            )

        # 2. Confirmation auto-reply to applicant
        cand_template = jinja_env.get_template("application_received.html")
        cand_html = cand_template.render(
            candidate_name=application.full_name,
            job_title=job_title,
        )

        send_smtp_email(
            to_email=application.email,
            subject=f"Application Received: {job_title}",
            html_content=cand_html,
            db=db,
        )
    finally:
        db.close()

def send_contact_email_task(contact_id: int) -> None:
    """Background task to notify HR of a new contact message."""
    db = SessionLocal()
    try:
        contact = db.query(ContactMessage).filter(ContactMessage.id == contact_id).first()
        if not contact:
            logger.error(f"Contact message #{contact_id} not found for email notification.")
            return

        hr_email = get_hr_recipient_email(db)
        if not hr_email:
            return

        template = jinja_env.get_template("new_message.html")
        html_content = template.render(
            name=contact.name,
            email=contact.email,
            subject=contact.subject,
            message=contact.message,
            created_at=contact.created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if contact.created_at else "",
        )

        send_smtp_email(
            to_email=hr_email,
            subject=f"New Contact Inquiry: {contact.subject}",
            html_content=html_content,
            db=db,
        )
    finally:
        db.close()

def send_newsletter_broadcast_task(post_id: int) -> None:
    """Broadcast an email newsletter notification to all active subscribers for a published article."""
    db = SessionLocal()
    try:
        post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
        if not post or post.status != PostStatus.published:
            return

        subscribers = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.is_active == True).all()
        if not subscribers:
            logger.info("No active newsletter subscribers to notify.")
            return

        article_url = f"http://localhost:3000/blog/{post.slug}"
        author_name = post.author_name or (post.author.name if post.author else "SeQuenX Editorial")

        newsletter_html = f"""
        <div style="font-family: Arial, Helvetica, sans-serif; max-width: 620px; margin: 0 auto; padding: 28px; color: #1e293b; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;">
          <div style="border-bottom: 2px solid #315bea; padding-bottom: 16px; margin-bottom: 24px;">
            <span style="font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.08em; color: #315bea;">SeQuenX Journal &bull; New Article</span>
            <h1 style="font-size: 22px; font-weight: 800; color: #0B1F42; margin: 8px 0 0;">{post.title}</h1>
          </div>

          <p style="font-size: 14px; line-height: 1.6; color: #475569; margin-bottom: 20px;">
            {post.excerpt or 'We have published a new engineering and software delivery article on the SeQuenX Journal. Check it out to stay ahead with technical insights.'}
          </p>

          <div style="background: #f8fafc; border-left: 4px solid #315bea; padding: 12px 16px; border-radius: 4px; margin: 20px 0; font-size: 12px; color: #64748b;">
            <span>By <strong>{author_name}</strong></span> &bull; <span>{post.read_time or '5 min read'}</span> &bull; <span>Category: {post.category or 'Engineering'}</span>
          </div>

          <div style="margin: 28px 0; text-align: center;">
            <a href="{article_url}" style="background: #1a56db; color: #ffffff; padding: 12px 28px; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block;">
              Read Full Article &rarr;
            </a>
          </div>

          <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 32px 0 16px;" />

          <p style="font-size: 11px; color: #94a3b8; text-align: center; margin: 0; line-height: 1.5;">
            You received this email because you subscribed to the SeQuenX Journal newsletter.<br/>
            SeQuenX &bull; Modern Enterprise Software Development &amp; Remote Engineering
          </p>
        </div>
        """

        subject = f"New Article: {post.title} | SeQuenX Journal"

        for sub in subscribers:
            send_smtp_email(
                to_email=sub.email,
                subject=subject,
                html_content=newsletter_html,
                db=db,
            )

        logger.info(f"Broadcasted new blog post '{post.title}' to {len(subscribers)} subscribers.")
    except Exception as exc:
        logger.error(f"Error in send_newsletter_broadcast_task: {exc}", exc_info=True)
    finally:
        db.close()
