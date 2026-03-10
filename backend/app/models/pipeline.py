"""Pipeline run model."""

import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    status = Column(String(50), default="running")  # running, completed, failed
    products_discovered = Column(Integer, default=0)
    products_scored = Column(Integer, default=0)
    top_products_count = Column(Integer, default=5)
    error_message = Column(Text)

    products = relationship("Product", backref="pipeline_run", foreign_keys="Product.pipeline_run_id")
