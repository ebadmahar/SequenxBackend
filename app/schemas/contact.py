from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    website: Optional[str] = None  # Honeypot field; must be empty

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "subject": "Business Partnership Inquiry",
                "message": "Hello, I would like to inquire about collaboration opportunities.",
                "website": "",
            }
        }
    )

class ContactMarkRead(BaseModel):
    is_read: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_read": True,
            }
        }
    )

class ContactOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    subject: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "subject": "Business Partnership Inquiry",
                "message": "Hello, I would like to inquire about collaboration opportunities.",
                "is_read": False,
                "created_at": "2026-10-29T15:00:00Z",
            }
        },
    )

class ContactListResponse(BaseModel):
    items: List[ContactOut]
    total: int
    page: int
    limit: int
    pages: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 8,
                "page": 1,
                "limit": 10,
                "pages": 1,
            }
        }
    )

