from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

class LoginRequest(BaseModel):
    username: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin@example.com",
                "password": "AdminPassword123!",
            }
        }
    )

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "role": "admin",
            }
        }
    )

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

