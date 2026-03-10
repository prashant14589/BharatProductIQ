# SYSTEM_ARCHITECTURE.md

## Overview

IndiaFind is an **agentic AI pipeline** built on a modular service architecture. Each agent is an independent Python module with a defined input schema, output schema, and AI prompt strategy. Agents are orchestrated via Celery Beat on a 12-hour cron schedule.

---

## Architecture Layers

```
┌──────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                              │
│  Next.js 14 App Router + Tailwind CSS + ShadCN UI               │
│  REST API calls to FastAPI backend                               │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTP/JSON
┌────────────────────────────▼─────────────────────────────────────┐
│  API LAYER                                                       │
│  FastAPI (Python 3.11)                                           │
│  Routes: /products, /agents, /pipeline, /creatives              │
│  Auth: API key middleware (future: JWT)                          │
└──────────┬────────────────────────────────────┬──────────────────┘
           │                                    │
┌──────────▼────────────┐          ┌────────────▼─────────────────┐
│  TASK QUEUE LAYER     │          │  CACHE LAYER                 │
│  Celery + Redis       │          │  Redis (TTL: 1hr per product) │
│  Celery Beat cron     │          │  Pipeline status tracking     │
└──────────┬────────────┘          └──────────────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────────┐
│  AGENT ORCHESTRATION LAYER                                       │
│  Pipeline Runner → chains agents sequentially                   │
│  Each agent is a Python class with .run(input) → output         │
└──────────┬──────────────────────────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────────┐
│  AGENT LAYER (7 agents)                                          │
│                                                                  │
│  TrendAgent → MarketAgent → SupplierAgent → ProfitAgent         │
│       → ScoringAgent → CreativeAgent → ShopifyAgent             │
│                                                                  │
│  Each agent uses: LLM (Claude/GPT) + Web scraping/APIs         │
└──────────┬──────────────────────────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────────┐
│  DATA LAYER                                                      │
│  PostgreSQL 15 (primary store)                                   │
│  Tables: products, trend_signals, suppliers, profit_models,     │
│          ad_creatives, shopify_pages, pipeline_runs             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Pipeline Flow

```
TRIGGER (Celery Beat — every 12 hours)
         │
         ▼
[1] TrendAgent.run()
    Input:  { sources: ["tiktok","amazon_us","aliexpress","reddit"] }
    Output: List[ProductCandidate]
    Filter: top 20 by trend_score
         │
         ▼
[2] MarketAgent.run(product_candidates)
    Input:  List[ProductCandidate]
    Output: List[ProductCandidate + india_market_data]
    Filter: india_saturation_score < 60
         │
         ▼
[3] SupplierAgent.run(filtered_candidates)
    Input:  List[ProductCandidate]
    Output: List[ProductCandidate + supplier_data]
    Filter: unit_cost found
         │
         ▼
[4] ProfitAgent.run(candidates_with_suppliers)
    Input:  List[ProductCandidate + supplier_data]
    Output: List[ProductCandidate + profit_model]
    Filter: estimated_margin >= 40%
         │
         ▼
[5] ScoringAgent.run(profitable_candidates)
    Input:  List[ProductCandidate + full_data]
    Output: List[ScoredProduct]
    Filter: score >= 70
         │
         ▼
[6] CreativeAgent.run(scored_products)    [7] ShopifyAgent.run(scored_products)
    Output: ad_creatives                       Output: shopify_pages
         │                                          │
         └──────────────┬───────────────────────────┘
                        ▼
              Save to PostgreSQL
              Invalidate Redis cache
              Notify via webhook (optional)
```

---

## Key Design Decisions

### 1. Agent Isolation
Each agent has no direct dependency on other agents' internals. Communication is via typed Python dataclasses (Pydantic models). This allows swapping any agent's underlying implementation without breaking the pipeline.

### 2. LLM Usage Strategy
Agents use the LLM for tasks that require reasoning and language:
- Trend scoring rationale
- Market analysis narrative
- Creative generation
- Shopify copy

Structured data (prices, URLs, counts) is fetched from APIs/scrapers and **not** delegated to the LLM to avoid hallucination.

### 3. Fail-Safe Pipeline
If an agent fails for a specific product, that product is **skipped** (logged), not the entire pipeline. The pipeline uses try/except per product in each agent.

### 4. Data Freshness
- Pipeline runs every 12 hours
- Redis TTL: 1 hour for product list cache
- PostgreSQL is the source of truth
- Frontend always fetches from cache, falls back to DB

### 5. Extensibility
Adding a new agent requires:
1. Create `/agents/new_agent/agent.py` inheriting from `BaseAgent`
2. Add to pipeline runner's chain
3. Add DB columns or table if needed
4. Done — no changes to API or frontend needed for data storage

---

## Infrastructure

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   nginx     │  │  Next.js    │  │   FastAPI   │  │  Celery     │
│  (reverse   │  │  :3000      │  │  :8000      │  │  Worker     │
│   proxy)    │  │             │  │             │  │             │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                 │
       └────────────────┴────────────────┴─────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
             ┌──────▼──────┐         ┌────────▼────────┐
             │ PostgreSQL  │         │     Redis        │
             │  :5432      │         │     :6379        │
             └─────────────┘         └─────────────────┘
```

All services run as Docker containers defined in `docker-compose.yml`.