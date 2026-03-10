# Database Schema — BharatProductIQ

## 1. Overview

PostgreSQL 15+ with Alembic migrations. Redis used for caching and Celery broker.

---

## 2. Entity Relationship Diagram

```
┌──────────────┐       ┌───────────────┐       ┌──────────────┐
│   products   │───┬───│ trend_signals │       │  suppliers   │
└──────────────┘   │   └───────────────┘       └──────────────┘
        │          │          │                        │
        │          │          │                        │
        │   ┌──────┴──────────┴──────┐                 │
        │   │   market_gaps          │                 │
        │   └────────────────────────┘                 │
        │                                              │
        │   ┌──────────────────────┐    ┌──────────────┴────┐
        ├───│   profit_models      │    │ product_suppliers  │
        │   └──────────────────────┘    └───────────────────┘
        │
        │   ┌──────────────────────┐
        ├───│   product_scores     │
        │   └──────────────────────┘
        │
        │   ┌──────────────────────┐
        ├───│   ad_creatives       │
        │   └──────────────────────┘
        │
        └───│   shopify_pages      │
            └──────────────────────┘
```

---

## 3. Tables

### `products`

Core product entity. One row per discovered product.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| external_id | VARCHAR(255) | UNIQUE, INDEX | ID from source (e.g. AliExpress) |
| product_name | VARCHAR(500) | NOT NULL | Display name |
| category | VARCHAR(255) | INDEX | Product category |
| product_images | JSONB | | Array of image URLs |
| video_links | JSONB | | Array of video URLs |
| status | VARCHAR(50) | DEFAULT 'pending' | pending, processing, scored, rejected |
| pipeline_run_id | UUID | FK | Reference to pipeline run |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

### `trend_signals`

Trend data per product (1:1 or 1:N).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| product_id | UUID | FK, UNIQUE | |
| trend_score | INTEGER | CHECK 0-100 | |
| trend_sources | JSONB | | ["tiktok","amazon_us",...] |
| raw_signals | JSONB | | Raw API responses |
| created_at | TIMESTAMPTZ | | |

### `market_gaps`

India market analysis per product.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| product_id | UUID | FK, UNIQUE | |
| india_saturation_score | INTEGER | 0-100 | |
| competitor_count | INTEGER | | |
| average_price_inr | DECIMAL(12,2) | | |
| brand_presence | VARCHAR(50) | | low, medium, high |
| opportunity_score | INTEGER | 0-100 | |
| top_competitors | JSONB | | |
| created_at | TIMESTAMPTZ | | |

### `suppliers`

Supplier records (can be shared across products).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| supplier_name | VARCHAR(255) | | |
| supplier_url | VARCHAR(500) | | |
| platform | VARCHAR(100) | | alibaba, aliexpress, cj, 1688 |
| unit_cost_usd | DECIMAL(10,2) | | |
| unit_cost_inr | DECIMAL(12,2) | | |
| shipping_cost_inr | DECIMAL(12,2) | | |
| moq | INTEGER | | |
| white_label_available | BOOLEAN | | |
| lead_time_days | INTEGER | | |
| created_at | TIMESTAMPTZ | | |

### `product_suppliers`

Many-to-many: products ↔ suppliers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| product_id | UUID | FK, PK | |
| supplier_id | UUID | FK, PK | |
| is_primary | BOOLEAN | DEFAULT false | Preferred supplier |
| created_at | TIMESTAMPTZ | | |

### `profit_models`

Profitability calculation per product.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| product_id | UUID | FK, UNIQUE | |
| unit_cost_inr | DECIMAL(12,2) | | |
| shipping_cost_inr | DECIMAL(12,2) | | |
| ad_cost_per_unit_inr | DECIMAL(12,2) | | |
| total_cost_inr | DECIMAL(12,2) | | |
| suggested_price_inr | DECIMAL(12,2) | | |
| estimated_margin_pct | DECIMAL(5,2) | | |
| price_in_range | BOOLEAN | | 799-2499 |
| created_at | TIMESTAMPTZ | | |

### `product_scores`

Final 0-100 score and breakdown.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| product_id | UUID | FK, UNIQUE | |
| total_score | INTEGER | CHECK 0-100 | |
| score_breakdown | JSONB | | {trend, india_gap, margin, visual, logistics} |
| created_at | TIMESTAMPTZ | | |

### `ad_creatives`

Generated ad content.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| product_id | UUID | FK, UNIQUE | |
| ad_hooks | JSONB | | Array of strings |
| short_form_scripts | JSONB | | Array of {platform, script, duration} |
| marketing_angles | JSONB | | Array of strings |
| meta_targeting | JSONB | | Interests, behaviors, locations |
| created_at | TIMESTAMPTZ | | |

### `shopify_pages`

Generated Shopify page content.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| product_id | UUID | FK, UNIQUE | |
| product_title | VARCHAR(255) | | |
| product_description | TEXT | | |
| benefit_bullets | JSONB | | Array of strings |
| faqs | JSONB | | Array of {question, answer} |
| upsell_suggestions | JSONB | | Array of strings |
| meta_title | VARCHAR(255) | | |
| meta_description | VARCHAR(500) | | |
| created_at | TIMESTAMPTZ | | |

### `pipeline_runs`

Audit trail for each pipeline execution.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | |
| started_at | TIMESTAMPTZ | | |
| completed_at | TIMESTAMPTZ | | |
| status | VARCHAR(50) | | running, completed, failed |
| products_discovered | INTEGER | | |
| products_scored | INTEGER | | |
| top_products_count | INTEGER | | |
| error_message | TEXT | | |

---

## 4. Indexes

```sql
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_created_at ON products(created_at DESC);
CREATE INDEX idx_product_scores_total ON product_scores(total_score DESC);
CREATE INDEX idx_pipeline_runs_started ON pipeline_runs(started_at DESC);
```

---

## 5. Redis Keys (Caching)

| Key | TTL | Description |
|-----|-----|-------------|
| `dashboard:top_products` | 1h | Top 5–10 products for dashboard |
| `product:{id}` | 6h | Full product with all enrichment |
| `trend:cache:{hash}` | 6h | Cached trend API responses |
