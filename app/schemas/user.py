from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.editor
    avatar: Optional[str] = None
    role_title: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    current_password: Optional[str] = None
    role: Optional[UserRole] = None
    avatar: Optional[str] = None
    role_title: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    avatar: Optional[str] = None
    role_title: Optional[str] = None
    bio: Optional[str] = None
    must_change_password: bool = False
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class UserListResponse(BaseModel):
    items: list[UserOut]
    total: int
    page: int
    limit: int
    pages: int
