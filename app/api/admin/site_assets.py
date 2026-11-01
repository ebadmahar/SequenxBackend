from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.site_asset import SiteAsset
from app.models.user import User, UserRole
from app.schemas.site_asset import SiteAssetListResponse, SiteAssetOut, SiteAssetUpdate
from app.services.file_service import delete_custom_site_asset, save_site_asset_file

router = APIRouter(
    prefix="/admin/site-assets",
    tags=["Admin Site Assets"],
    dependencies=[Depends(require_roles(UserRole.admin, UserRole.editor))],
)

@router.get(
    "",
    response_model=SiteAssetListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all site assets with page filtering",
)
def list_site_assets(
    page: Optional[str] = Query(None, description="Filter by page category"),
    search: Optional[str] = Query(None, description="Search keyword or key"),
    db: Session = Depends(get_db),
):
    query = db.query(SiteAsset)

    if page and page.lower() != "all":
        query = query.filter(SiteAsset.page == page.lower())

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            or_(
                SiteAsset.key.ilike(search_filter),
                SiteAsset.location_keyword.ilike(search_filter),
                SiteAsset.alt_text.ilike(search_filter),
            )
        )

    # Fetch unique pages for tab navigation
    all_pages = [p[0] for p in db.query(SiteAsset.page).distinct().all()]

    items = query.order_by(SiteAsset.page.asc(), SiteAsset.key.asc()).all()
    return SiteAssetListResponse(
        items=items,
        total=len(items),
        pages=all_pages,
    )

@router.get(
    "/{key}",
    response_model=SiteAssetOut,
    status_code=status.HTTP_200_OK,
    summary="Get single asset detail",
)
def get_site_asset(key: str, db: Session = Depends(get_db)):
    asset = db.query(SiteAsset).filter(SiteAsset.key == key).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{key}' not found",
        )
    return asset

@router.post(
    "/{key}/upload",
    response_model=SiteAssetOut,
    status_code=status.HTTP_200_OK,
    summary="Upload new image/svg for a site asset",
)
async def upload_site_asset(
    key: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.editor)),
):
    asset = db.query(SiteAsset).filter(SiteAsset.key == key).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{key}' not found",
        )

    # If asset already had a custom file uploaded, clean it up
    if asset.current_url:
        delete_custom_site_asset(asset.current_url)

    new_url = await save_site_asset_file(file, key)
    asset.current_url = new_url
    asset.updated_by = current_user.email
    db.commit()
    db.refresh(asset)
    return asset

@router.post(
    "/{key}/reset",
    response_model=SiteAssetOut,
    status_code=status.HTTP_200_OK,
    summary="Reset asset to factory default",
)
def reset_site_asset(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.editor)),
):
    asset = db.query(SiteAsset).filter(SiteAsset.key == key).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{key}' not found",
        )

    if asset.current_url:
        delete_custom_site_asset(asset.current_url)
        asset.current_url = None
        asset.updated_by = current_user.email
        db.commit()
        db.refresh(asset)

    return asset

@router.patch(
    "/{key}",
    response_model=SiteAssetOut,
    status_code=status.HTTP_200_OK,
    summary="Update asset metadata",
)
def update_site_asset(
    key: str,
    payload: SiteAssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.editor)),
):
    asset = db.query(SiteAsset).filter(SiteAsset.key == key).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{key}' not found",
        )

    if payload.alt_text is not None:
        asset.alt_text = payload.alt_text.strip()

    asset.updated_by = current_user.email
    db.commit()
    db.refresh(asset)
    return asset

