from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.setting import Setting
from app.models.user import User, UserRole
from app.schemas.setting import SettingOut, SettingsBulkUpdate, SettingUpdate

router = APIRouter(prefix="/admin/settings", tags=["Admin Settings"])

@router.get(
    "",
    response_model=List[SettingOut],
    status_code=status.HTTP_200_OK,
    summary="List all application settings",
    description="Retrieve all configurable platform settings. Restricted strictly to administrators.",
)
def list_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    return db.query(Setting).order_by(Setting.key.asc()).all()

@router.get(
    "/{key}",
    response_model=SettingOut,
    status_code=status.HTTP_200_OK,
    summary="Get setting by key",
    description="Retrieve the value and metadata of a specific setting key.",
)
def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting key '{key}' not found",
        )
    return setting

@router.put(
    "/{key}",
    response_model=SettingOut,
    status_code=status.HTTP_200_OK,
    summary="Update single setting value",
    description="Update the configuration value for a specific setting key (e.g., 'hr_email').",
)
def update_single_setting(
    key: str,
    payload: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        setting = Setting(key=key, value=payload.value)
        db.add(setting)
    else:
        setting.value = payload.value

    db.commit()
    db.refresh(setting)
    return setting

@router.put(
    "",
    response_model=List[SettingOut],
    status_code=status.HTTP_200_OK,
    summary="Bulk update settings",
    description="Update multiple settings simultaneously using a key-value dictionary.",
)
def update_multiple_settings(
    payload: SettingsBulkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    updated = []
    for key, value in payload.settings.items():
        setting = db.query(Setting).filter(Setting.key == key).first()
        if not setting:
            setting = Setting(key=key, value=value)
            db.add(setting)
        else:
            setting.value = value
        updated.append(setting)

    db.commit()
    for s in updated:
        db.refresh(s)
    return updated

