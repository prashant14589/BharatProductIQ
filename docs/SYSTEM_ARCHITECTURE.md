# System Architecture — BharatProductIQ

## 1. Overview

BharatProductIQ is an **agentic AI platform** for ecommerce product discovery in the Indian market. The system orchestrates multiple specialized agents through a pipeline that filters, scores, and enriches product opportunities.

---

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                                    │
│  Next.js App (React) │ Tailwind CSS │ Server Components │ API Client              │
└──────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ HTTP / WebSocket
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                API LAYER (FastAPI)                                 │
│  REST Endpoints │ WebSocket │ Auth (JWT) │ Rate Limiting │ CORS                    │
└──────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              ORCHESTRATION LAYER                                   │
│  Celery Tasks │ Pipeline Coordinator │ Job Scheduler (Celery Beat)                 │
└──────────────────────────────────────────────────────────────────────────────────┘
                                          │
          ┌───────────────────────────────┼───────────────────────────────┐
          ▼                               ▼                               ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   TREND AGENT       │     │   MARKET AGENT      │     │   SUPPLIER AGENT     │
│   (Global signals)  │     │   (India focus)     │     │   (Source discovery) │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
          │                               │                               │
          └───────────────────────────────┼───────────────────────────────┘
                                          │
          ┌───────────────────────────────┼───────────────────────────────┐
          ▼                               ▼                               ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   PROFIT AGENT      │     │   SCORING AGENT     │     │   CREATIVE AGENT     │
│   (Margin calc)     │     │   (0–100 score)     │     │   (Ads / scripts)    │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│   SHOPIFY AGENT (Product page content generation)                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                            │
│  PostgreSQL (primary) │ Redis (cache, queues) │ External APIs (scraping, AI)       │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Agent Pipeline Flow

```
   ┌──────────┐
   │  CRON    │  Every 12 hours
   │  TRIGGER │
   └────┬─────┘
        │
        ▼
┌───────────────────┐
│ 1. TREND AGENT    │  Scans TikTok, Amazon US, AliExpress, Reddit, FB Ad Library, G Trends
│    Output: Raw    │  → product_name, trend_score, trend_sources, images, videos
│    trending items │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 2. MARKET AGENT   │  Checks Amazon IN, Flipkart, Meesho, D2C
│    Output: India  │  → india_saturation_score, competitor_count, avg_price, brand_presence
│    gap analysis   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 3. SUPPLIER       │  Searches Alibaba, AliExpress, CJ, 1688
│    AGENT          │  → supplier_links, unit_cost, shipping, MOQ, white_label
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 4. PROFIT AGENT   │  Calculates: total_cost, suggested_price, estimated_margin
│    Output: Margin │  FILTER: margin < 40% → DROP
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 5. SCORING AGENT  │  Weights: trend, india_gap, margin, visual_demo, logistics
│    Output: 0-100  │  FILTER: score < 70 → DROP
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 6. CREATIVE AGENT │  Generates: hooks, video scripts, angles, Meta targeting
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ 7. SHOPIFY AGENT  │  Generates: title, description, bullets, FAQs, upsells
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ DASHBOARD         │  Top 5 (configurable) pushed to frontend
│ (Top Opportunities)│
└───────────────────┘
```

---

## 4. Data Flow

| Stage   | Input                      | Output                                      |
|---------|----------------------------|---------------------------------------------|
| Trend   | External APIs / scrapers   | `products`, `trend_signals`                 |
| Market  | Product identifiers        | `market_gaps` (India saturation)            |
| Supplier| Product keywords           | `suppliers`                                 |
| Profit  | Cost + shipping + ad est.  | `profit_models`                             |
| Score   | All signals                | `product_scores`                            |
| Creative| Product + market context   | `ad_creatives`                              |
| Shopify | Product + benefits         | `shopify_pages`                             |

---

## 5. Component Responsibilities

### Backend (FastAPI)

- **API**: CRUD for products, runs pipelines, serves dashboard data
- **Auth**: JWT-based (future SaaS)
- **Workers**: Celery for async agent execution
- **Scheduler**: Celery Beat for 12h scan schedule

### Agents

- Each agent is a **Python module** with `run(product_context) -> output_schema`
- Agents are **stateless** and receive context from the orchestrator
- Agents call **external APIs** (OpenAI/Claude, scrapers) and return structured data

### Frontend

- **Next.js 14+** with App Router
- **Tailwind CSS** for styling
- **Server Components** for initial load, client for interactivity
- Product cards → product detail modal with all enrichment

---

## 6. Scaling Considerations

- **Horizontal**: Celery workers scale by adding more worker processes
- **Database**: Read replicas for dashboard queries; writes to primary
- **Cache**: Redis for product list, trend scores (TTL 1–6h)
- **Rate limits**: Throttle external API calls (TikTok, Facebook, etc.)

---

## 7. Security

- API keys in env, never in code
- Rate limiting on public endpoints
- Input validation (Pydantic) on all inputs
- CORS restricted to frontend origin in production
