# Agent Specifications — BharatProductIQ

## 1. Trend Detection Agent

**Purpose**: Identify globally trending products from multiple signals.

### Inputs
- None (scheduled scan) or `keywords` (manual trigger)

### Data Sources
| Source | Method | Output Fields |
|--------|--------|---------------|
| TikTok | API / scrape | viral_products, video_links |
| Amazon US | Best sellers API | product_name, rank, category |
| AliExpress | Trending API | product_name, orders, images |
| Reddit | r/entrepreneur, r/dropship | product mentions, sentiment |
| Facebook Ad Library | Meta API | active ads, creatives |
| Google Trends | pytrends / API | search_interest, related_queries |

### Output Schema
```json
{
  "product_name": "string",
  "trend_score": 0-100,
  "trend_sources": ["tiktok", "amazon_us", "aliexpress", "reddit", "facebook", "google_trends"],
  "product_images": ["url1", "url2"],
  "video_links": ["url1"],
  "category": "string",
  "raw_signals": {}
}
```

### Logic
- Aggregate signals into a single `trend_score` (0–100)
- Weight TikTok/Reels higher for visual-demo products
- Emit products with `trend_score >= 50`

---

## 2. Market Gap Agent (India Focus)

**Purpose**: Assess Indian ecommerce market saturation and opportunity.

### Inputs
- `product_name`
- `category`
- `product_images` (optional, for visual search)

### Data Sources
| Source | Method | Output Fields |
|--------|--------|---------------|
| Amazon India | Product Search API / scrape | listing_count, avg_price, top_sellers |
| Flipkart | Search API / scrape | listing_count, avg_price |
| Meesho | Search / scrape | presence, price_range |
| D2C websites | Keyword search | brand_count, price_range |

### Output Schema
```json
{
  "india_saturation_score": 0-100,
  "competitor_count": 0-999,
  "average_price_inr": 0,
  "brand_presence": "low|medium|high",
  "opportunity_score": 0-100,
  "top_competitors": []
}
```

### Logic
- `india_saturation_score`: higher = more saturated (inverse of opportunity)
- `opportunity_score = 100 - india_saturation_score` (for downstream scoring)
- Prefer `brand_presence = low` and `competitor_count` < 50

---

## 3. Supplier Discovery Agent

**Purpose**: Find suppliers and sourcing options.

### Inputs
- `product_name`
- `category`
- `target_moq` (optional)

### Data Sources
| Source | Method | Output Fields |
|--------|--------|---------------|
| Alibaba | Search API | supplier_links, unit_cost, MOQ |
| AliExpress | Product search | unit_cost, shipping, MOQ |
| CJ Dropshipping | API | unit_cost, shipping, MOQ |
| 1688 | Scrape / proxy | unit_cost, MOQ, white_label |

### Output Schema
```json
{
  "supplier_links": ["url1", "url2"],
  "unit_cost_usd": 0,
  "unit_cost_inr": 0,
  "shipping_cost_inr": 0,
  "moq": 0,
  "white_label_available": true|false,
  "lead_time_days": 0,
  "supplier_ratings": []
}
```

### Logic
- Pick lowest `unit_cost` + `shipping_cost` combination meeting MOQ
- Prefer `white_label_available = true`

---

## 4. Profitability Agent

**Purpose**: Calculate profit model and filter by margin.

### Inputs
- `unit_cost_inr`
- `shipping_cost_inr`
- `estimated_ad_cost_per_unit` (default: ₹150–200)
- `platform_fee_pct` (default: 5%)
- `gst_pct` (18% where applicable)

### Output Schema
```json
{
  "total_cost_inr": 0,
  "suggested_price_inr": 0,
  "estimated_margin_pct": 0,
  "break_even_units": 0,
  "price_in_range_799_2499": true|false
}
```

### Logic
- `total_cost = unit_cost + shipping + ad_cost + (platform_fee + GST)`
- `suggested_price = total_cost / (1 - target_margin)`, target_margin ≥ 0.40
- **Filter**: Drop if `estimated_margin_pct < 40`
- **Filter**: Prefer `suggested_price` in ₹799–₹2499

---

## 5. Product Scoring Agent

**Purpose**: Aggregate all signals into a single 0–100 score.

### Inputs
- `trend_score`
- `india_opportunity_score`
- `profit_margin_pct`
- `visual_demo_potential` (0–100, from images/videos)
- `logistics_feasibility` (0–100, MOQ, lead time, white label)

### Output Schema
```json
{
  "total_score": 0-100,
  "score_breakdown": {
    "trend_signal": 0-100,
    "india_gap": 0-100,
    "profit_margin": 0-100,
    "visual_demo_potential": 0-100,
    "logistics_feasibility": 0-100
  },
  "weights_used": {}
}
```

### Logic
- Weighted sum: trend 25%, india_gap 25%, margin 20%, visual 20%, logistics 10%
- **Filter**: Surface only products with `total_score >= 70`

---

## 6. Creative Intelligence Agent

**Purpose**: Generate ad hooks, scripts, and targeting.

### Inputs
- `product_name`
- `category`
- `benefits` (from manual or inferred)
- `target_audience` (India, age 18–45)
- `platform` (Meta, TikTok)

### Output Schema
```json
{
  "ad_hooks": ["hook1", "hook2", "hook3"],
  "short_form_scripts": [
    {
      "platform": "tiktok|reels",
      "script": "string",
      "duration_seconds": 15
    }
  ],
  "marketing_angles": ["angle1", "angle2"],
  "meta_targeting": {
    "interests": [],
    "behaviors": [],
    "custom_audiences": [],
    "age_range": [18, 45],
    "locations": ["India"]
  }
}
```

### Logic
- Use OpenAI/Claude with structured prompts
- Hooks should be < 10 words, curiosity-driven
- Scripts 15–30 seconds, CTA at end

---

## 7. Shopify Page Generator Agent

**Purpose**: Generate ecommerce-ready product page content.

### Inputs
- `product_name`
- `category`
- `benefits`
- `specs` (if available)
- `competitor_descriptions` (optional)

### Output Schema
```json
{
  "product_title": "string",
  "product_description": "string",
  "benefit_bullets": ["bullet1", "bullet2"],
  "faqs": [
    { "question": "string", "answer": "string" }
  ],
  "upsell_suggestions": ["product1", "product2"],
  "meta_title": "string",
  "meta_description": "string"
}
```

### Logic
- Title: SEO-friendly, under 70 chars
- Description: Problem–solution–benefit structure
- Bullets: 5–7, benefit-focused
- FAQs: 3–5 common objections

---

## Extensibility: Future Agents

| Agent | Purpose | Plug Point |
|-------|---------|------------|
| Ad Spy Agent | Pull competitor ad creatives from Meta/TikTok | After Creative Agent |
| Competitor Store Analyzer | Analyze Shopify/Woo stores | After Market Agent |
| Influencer Trend Detector | Track influencer promotions | Parallel to Trend Agent |
| Price Arbitrage Agent | Compare cross-platform prices | After Supplier Agent |

Agents are registered in `agents/registry.py` and invoked by the pipeline orchestrator.
