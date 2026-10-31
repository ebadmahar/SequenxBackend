import os
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_ROOT = BASE_DIR / settings.UPLOAD_DIR
CVS_DIR = UPLOADS_ROOT / "cvs"
BLOG_IMAGES_DIR = UPLOADS_ROOT / "blog_images"

ALLOWED_CV_EXTENSIONS = {".pdf", ".doc", ".docx"}
ALLOWED_CV_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",
}
MAX_CV_SIZE = settings.MAX_CV_SIZE_MB * 1024 * 1024

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_IMAGE_SIZE = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024

def ensure_upload_dirs() -> None:
    """Ensure upload directories for CVs and blog images exist."""
    CVS_DIR.mkdir(parents=True, exist_ok=True)
    BLOG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

async def save_cv_file(file: UploadFile) -> str:
    """Validate and store an uploaded CV file with a secure random UUID name."""
    ensure_upload_dirs()

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing",
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_CV_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(ALLOWED_CV_EXTENSIONS)}",
        )

    if file.content_type and file.content_type.lower() not in ALLOWED_CV_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file content type '{file.content_type}'.",
        )

    content = await file.read()
    if len(content) > MAX_CV_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CV file exceeds maximum permitted size of {settings.MAX_CV_SIZE_MB}MB.",
        )

    unique_filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = CVS_DIR / unique_filename

    with open(dest_path, "wb") as f:
        f.write(content)

    return f"{settings.UPLOAD_DIR}/cvs/{unique_filename}"

async def save_blog_image(file: UploadFile) -> str:
    """Validate and store an uploaded blog image with a secure random UUID name."""
    ensure_upload_dirs()

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image filename is missing",
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image format '{ext}'. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
        )

    if file.content_type and file.content_type.lower() not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image content type '{file.content_type}'.",
        )

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image exceeds maximum permitted size of {settings.MAX_IMAGE_SIZE_MB}MB.",
        )

    unique_filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = BLOG_IMAGES_DIR / unique_filename

    with open(dest_path, "wb") as f:
        f.write(content)

    return f"/static/blog_images/{unique_filename}"

def resolve_safe_cv_path(relative_cv_path: str) -> Path:
    """Resolve and verify that the CV file path is within the designated private directory."""
    target_path = (BASE_DIR / relative_cv_path).resolve()
    cvs_resolved = CVS_DIR.resolve()

    if not str(target_path).startswith(str(cvs_resolved)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access to file path is forbidden",
        )

    if not target_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV document not found on server",
        )

    return target_path

