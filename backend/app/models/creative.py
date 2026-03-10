"""Creative and Shopify page models."""

import uuid
from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AdCreative(Base):
    __tablename__ = "ad_creatives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), unique=True)
    ad_hooks = Column(JSONB, default=list)
    short_form_scripts = Column(JSONB, default=list)
    marketing_angles = Column(JSONB, default=list)
    meta_targeting = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="ad_creative")


class ShopifyPage(Base):
    __tablename__ = "shopify_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), unique=True)
    product_title = Column(String(255))
    product_description = Column(Text)
    benefit_bullets = Column(JSONB, default=list)
    faqs = Column(JSONB, default=list)
    upsell_suggestions = Column(JSONB, default=list)
    meta_title = Column(String(255))
    meta_description = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="shopify_page")
