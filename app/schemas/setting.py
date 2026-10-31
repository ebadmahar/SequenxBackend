from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict

class SettingUpdate(BaseModel):
    value: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "value": "careers@example.com",
            }
        }
    )

class SettingOut(BaseModel):
    id: int
    key: str
    value: Optional[str] = None
    description: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "key": "hr_email",
                "value": "careers@example.com",
                "description": "Recipient email address for job applications and contact notifications",
                "updated_at": "2026-10-29T16:00:00Z",
            }
        },
    )

class SettingsBulkUpdate(BaseModel):
    settings: Dict[str, str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "settings": {
                    "hr_email": "careers@example.com",
                    "company_name": "FrontSeq Solutions",
                }
            }
        }
    )

