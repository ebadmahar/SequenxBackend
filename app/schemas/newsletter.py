from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

class NewsletterSubscribeIn(BaseModel):
    email: EmailStr

class NewsletterSubscriberOut(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NewsletterSubscribersListResponse(BaseModel):
    items: List[NewsletterSubscriberOut]
    total: int

