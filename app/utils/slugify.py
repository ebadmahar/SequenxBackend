import re
import unicodedata
from typing import Optional
from sqlalchemy.orm import Session

def generate_slug(text: str) -> str:
    """Convert arbitrary text into a URL-friendly slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text or "item"

def generate_unique_slug(
    db: Session,
    model_class,
    title: str,
    current_id: Optional[int] = None,
) -> str:
    """Generate a unique slug for a model by appending numbers if needed."""
    base_slug = generate_slug(title)
    unique_slug = base_slug
    counter = 1

    while True:
        query = db.query(model_class).filter(model_class.slug == unique_slug)
        if current_id is not None:
            query = query.filter(model_class.id != current_id)
        existing = query.first()
        if not existing:
            return unique_slug

        unique_slug = f"{base_slug}-{counter}"
        counter += 1

