from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, computed_field

class SiteAssetBase(BaseModel):
    key: str
    page: str
    location_keyword: str
    asset_type: str
    aspect_ratio: str
    dimensions: str
    fallback_url: str
    alt_text: Optional[str] = None

class SiteAssetOut(SiteAssetBase):
    id: int
    current_url: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    @computed_field
    def active_url(self) -> str:
        return self.current_url if self.current_url else self.fallback_url

    @computed_field
    def is_customized(self) -> bool:
        return bool(self.current_url)

    model_config = ConfigDict(from_attributes=True)

class SiteAssetUpdate(BaseModel):
    alt_text: Optional[str] = None

class SiteAssetListResponse(BaseModel):
    items: List[SiteAssetOut]
    total: int
    pages: List[str]

class PublicAssetItem(BaseModel):
    url: str
    alt_text: Optional[str] = None
    aspect_ratio: str
    dimensions: str
