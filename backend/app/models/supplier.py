"""Supplier models."""

import uuid
from sqlalchemy import Column, String, Integer, Numeric, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_name = Column(String(255))
    supplier_url = Column(String(500))
    platform = Column(String(100))  # alibaba, aliexpress, cj, 1688
    unit_cost_usd = Column(Numeric(10, 2))
    unit_cost_inr = Column(Numeric(12, 2))
    shipping_cost_inr = Column(Numeric(12, 2))
    moq = Column(Integer)
    white_label_available = Column(Boolean)
    lead_time_days = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product_suppliers = relationship("ProductSupplier", back_populates="supplier")


class ProductSupplier(Base):
    __tablename__ = "product_suppliers"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), primary_key=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), primary_key=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="product_suppliers")
    supplier = relationship("Supplier", back_populates="product_suppliers")
