"""Product and related models."""

import uuid
from sqlalchemy import Column, String, Integer, Numeric, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


def uuid7():
    return uuid.uuid4().hex


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(255), unique=True, index=True)
    product_name = Column(String(500), nullable=False)
    category = Column(String(255), index=True)
    product_images = Column(JSONB, default=list)
    video_links = Column(JSONB, default=list)
    status = Column(String(50), default="pending")  # pending, processing, scored, rejected
    pipeline_run_id = Column(UUID(as_uuid=True), ForeignKey("pipeline_runs.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    trend_signal = relationship("TrendSignal", back_populates="product", uselist=False)
    market_gap = relationship("MarketGap", back_populates="product", uselist=False)
    profit_model = relationship("ProfitModel", back_populates="product", uselist=False)
    product_score = relationship("ProductScore", back_populates="product", uselist=False)
    ad_creative = relationship("AdCreative", back_populates="product", uselist=False)
    shopify_page = relationship("ShopifyPage", back_populates="product", uselist=False)
    product_suppliers = relationship("ProductSupplier", back_populates="product")


class TrendSignal(Base):
    __tablename__ = "trend_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), unique=True)
    trend_score = Column(Integer)  # 0-100
    trend_sources = Column(JSONB, default=list)
    raw_signals = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="trend_signal")


class MarketGap(Base):
    __tablename__ = "market_gaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), unique=True)
    india_saturation_score = Column(Integer)  # 0-100
    competitor_count = Column(Integer)
    average_price_inr = Column(Numeric(12, 2))
    brand_presence = Column(String(50))  # low, medium, high
    opportunity_score = Column(Integer)  # 0-100
    top_competitors = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="market_gap")


class ProfitModel(Base):
    __tablename__ = "profit_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), unique=True)
    unit_cost_inr = Column(Numeric(12, 2))
    shipping_cost_inr = Column(Numeric(12, 2))
    ad_cost_per_unit_inr = Column(Numeric(12, 2))
    total_cost_inr = Column(Numeric(12, 2))
    suggested_price_inr = Column(Numeric(12, 2))
    estimated_margin_pct = Column(Numeric(5, 2))
    price_in_range = Column(Boolean)  # 799-2499
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="profit_model")


class ProductScore(Base):
    __tablename__ = "product_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), unique=True)
    total_score = Column(Integer)  # 0-100
    score_breakdown = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="product_score")
