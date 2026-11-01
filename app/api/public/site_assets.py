from typing import Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.site_asset import SiteAsset
from app.schemas.site_asset import PublicAssetItem

router = APIRouter(prefix="/site-assets", tags=["Public Site Assets"])

@router.get(
    "",
    response_model=Dict[str, PublicAssetItem],
    status_code=status.HTTP_200_OK,
    summary="Get all public site assets map",
    description="Retrieve a map of all site assets with their active URLs for dynamic rendering.",
)
def get_public_site_assets(db: Session = Depends(get_db)):
    assets = db.query(SiteAsset).all()
    result = {}
    for asset in assets:
        result[asset.key] = PublicAssetItem(
            url=asset.current_url if asset.current_url else asset.fallback_url,
            alt_text=asset.alt_text,
            aspect_ratio=asset.aspect_ratio,
            dimensions=asset.dimensions,
        )
    return result
