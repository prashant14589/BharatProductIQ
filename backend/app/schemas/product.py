"""Product schemas."""

from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel


class ProductListItem(BaseModel):
    id: UUID
    product_name: str
    category: str | None
    status: str
    trend_score: int | None
    india_opportunity_score: int | None
    estimated_margin_pct: Decimal | None
    total_score: int | None
    supplier_link: str | None
    product_images: list[str] = []

    class Config:
        from_attributes = True


class ProductDetail(BaseModel):
    id: UUID
    product_name: str
    category: str | None
    product_images: list[str] = []
    video_links: list[str] = []
    status: str
    created_at: datetime
    updated_at: datetime

    trend_signals: dict | None = None
    market_gap: dict | None = None
    suppliers: list[dict] = []
    profit_model: dict | None = None
    product_score: dict | None = None
    ad_creatives: dict | None = None
    shopify_page: dict | None = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: list[ProductListItem]
    total: int
    limit: int
    offset: int
