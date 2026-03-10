# API Specification — BharatProductIQ

**Base URL**: `https://api.bharatproductiq.com/v1` (production)  
**Local**: `http://localhost:8000/v1`

---

## 1. Authentication (Future)

```
Authorization: Bearer <jwt_token>
```

Endpoints marked 🔒 require authentication.

---

## 2. Products

### `GET /products`

List products with optional filters.

**Query params**:
- `status`: pending | processing | scored | rejected
- `min_score`: integer 0-100
- `limit`: default 20, max 100
- `offset`: pagination

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "product_name": "string",
      "category": "string",
      "status": "string",
      "trend_score": 75,
      "india_opportunity_score": 80,
      "estimated_margin_pct": 45.5,
      "total_score": 78,
      "supplier_link": "https://..."
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

---

### `GET /products/{id}`

Get full product details including all enrichment.

**Response**:
```json
{
  "id": "uuid",
  "product_name": "string",
  "category": "string",
  "product_images": ["url1", "url2"],
  "video_links": ["url1"],
  "status": "string",
  "trend_signals": {
    "trend_score": 75,
    "trend_sources": ["tiktok", "amazon_us"]
  },
  "market_gap": {
    "india_saturation_score": 30,
    "competitor_count": 15,
    "average_price_inr": 1299,
    "opportunity_score": 70
  },
  "suppliers": [
    {
      "supplier_name": "string",
      "supplier_url": "url",
      "unit_cost_inr": 450,
      "shipping_cost_inr": 120,
      "moq": 10,
      "white_label_available": true
    }
  ],
  "profit_model": {
    "total_cost_inr": 720,
    "suggested_price_inr": 1299,
    "estimated_margin_pct": 44.6,
    "price_in_range": true
  },
  "product_score": {
    "total_score": 78,
    "score_breakdown": {}
  },
  "ad_creatives": {
    "ad_hooks": [],
    "short_form_scripts": [],
    "marketing_angles": [],
    "meta_targeting": {}
  },
  "shopify_page": {
    "product_title": "string",
    "product_description": "string",
    "benefit_bullets": [],
    "faqs": [],
    "upsell_suggestions": []
  },
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

---

### `POST /products/{id}/reject` 🔒

Mark product as rejected (manual filter).

**Response**: `204 No Content`

---

## 3. Pipeline

### `POST /pipeline/run`

Trigger a full pipeline run (manual).

**Request**:
```json
{
  "limit_trends": 50,
  "top_n": 5
}
```

**Response**:
```json
{
  "pipeline_run_id": "uuid",
  "status": "running",
  "message": "Pipeline started. Check /pipeline/runs/{id} for progress."
}
```

---

### `GET /pipeline/runs`

List pipeline runs.

**Query params**: `limit`, `offset`

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "started_at": "ISO8601",
      "completed_at": "ISO8601",
      "status": "completed",
      "products_discovered": 45,
      "products_scored": 12,
      "top_products_count": 5
    }
  ],
  "total": 10
}
```

---

### `GET /pipeline/runs/{id}`

Get pipeline run status and summary.

**Response**:
```json
{
  "id": "uuid",
  "started_at": "ISO8601",
  "completed_at": "ISO8601",
  "status": "completed",
  "products_discovered": 45,
  "products_scored": 12,
  "top_products_count": 5,
  "top_product_ids": ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"]
}
```

---

## 4. Dashboard

### `GET /dashboard/top-opportunities`

Returns top N scored products for dashboard. Cached in Redis.

**Query params**: `limit` (default 5)

**Response**:
```json
{
  "products": [
    {
      "id": "uuid",
      "product_name": "string",
      "trend_score": 75,
      "india_opportunity_score": 80,
      "estimated_margin_pct": 45.5,
      "total_score": 78,
      "supplier_link": "https://...",
      "product_images": ["url1"]
    }
  ],
  "cached_at": "ISO8601"
}
```

---

## 5. Health

### `GET /health`

**Response**:
```json
{
  "status": "ok",
  "database": "connected",
  "redis": "connected",
  "version": "1.0.0"
}
```

---

## 6. Error Response Format

```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "status_code": 400
}
```

Common codes: `VALIDATION_ERROR`, `NOT_FOUND`, `UNAUTHORIZED`, `RATE_LIMITED`, `INTERNAL_ERROR`
