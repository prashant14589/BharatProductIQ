"""Initial schema

Revision ID: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pipeline_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("products_discovered", sa.Integer(), nullable=True),
        sa.Column("products_scored", sa.Integer(), nullable=True),
        sa.Column("top_products_count", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("product_name", sa.String(500), nullable=False),
        sa.Column("category", sa.String(255), nullable=True),
        sa.Column("product_images", postgresql.JSONB(), nullable=True),
        sa.Column("video_links", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("pipeline_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["pipeline_run_id"], ["pipeline_runs.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_external_id", "products", ["external_id"], unique=True)
    op.create_index("ix_products_category", "products", ["category"], unique=False)
    op.create_index("ix_products_status", "products", ["status"], unique=False)

    op.create_table(
        "trend_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("trend_score", sa.Integer(), nullable=True),
        sa.Column("trend_sources", postgresql.JSONB(), nullable=True),
        sa.Column("raw_signals", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trend_signals_product_id", "trend_signals", ["product_id"], unique=True)

    op.create_table(
        "market_gaps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("india_saturation_score", sa.Integer(), nullable=True),
        sa.Column("competitor_count", sa.Integer(), nullable=True),
        sa.Column("average_price_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("brand_presence", sa.String(50), nullable=True),
        sa.Column("opportunity_score", sa.Integer(), nullable=True),
        sa.Column("top_competitors", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_market_gaps_product_id", "market_gaps", ["product_id"], unique=True)

    op.create_table(
        "suppliers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier_name", sa.String(255), nullable=True),
        sa.Column("supplier_url", sa.String(500), nullable=True),
        sa.Column("platform", sa.String(100), nullable=True),
        sa.Column("unit_cost_usd", sa.Numeric(10, 2), nullable=True),
        sa.Column("unit_cost_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("shipping_cost_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("moq", sa.Integer(), nullable=True),
        sa.Column("white_label_available", sa.Boolean(), nullable=True),
        sa.Column("lead_time_days", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "profit_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("unit_cost_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("shipping_cost_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("ad_cost_per_unit_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_cost_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("suggested_price_inr", sa.Numeric(12, 2), nullable=True),
        sa.Column("estimated_margin_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("price_in_range", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profit_models_product_id", "profit_models", ["product_id"], unique=True)

    op.create_table(
        "product_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("total_score", sa.Integer(), nullable=True),
        sa.Column("score_breakdown", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_scores_product_id", "product_scores", ["product_id"], unique=True)

    op.create_table(
        "product_suppliers",
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"],),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"],),
        sa.PrimaryKeyConstraint("product_id", "supplier_id"),
    )

    op.create_table(
        "ad_creatives",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ad_hooks", postgresql.JSONB(), nullable=True),
        sa.Column("short_form_scripts", postgresql.JSONB(), nullable=True),
        sa.Column("marketing_angles", postgresql.JSONB(), nullable=True),
        sa.Column("meta_targeting", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ad_creatives_product_id", "ad_creatives", ["product_id"], unique=True)

    op.create_table(
        "shopify_pages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_title", sa.String(255), nullable=True),
        sa.Column("product_description", sa.Text(), nullable=True),
        sa.Column("benefit_bullets", postgresql.JSONB(), nullable=True),
        sa.Column("faqs", postgresql.JSONB(), nullable=True),
        sa.Column("upsell_suggestions", postgresql.JSONB(), nullable=True),
        sa.Column("meta_title", sa.String(255), nullable=True),
        sa.Column("meta_description", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shopify_pages_product_id", "shopify_pages", ["product_id"], unique=True)


def downgrade() -> None:
    op.drop_table("shopify_pages")
    op.drop_table("ad_creatives")
    op.drop_table("product_suppliers")
    op.drop_table("product_scores")
    op.drop_table("profit_models")
    op.drop_table("suppliers")
    op.drop_table("market_gaps")
    op.drop_table("trend_signals")
    op.drop_table("products")
    op.drop_table("pipeline_runs")
