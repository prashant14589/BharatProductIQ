# BharatProductIQ — India-Focused Ecommerce Product Discovery Engine

> **AI-powered Product Discovery Platform** for identifying, evaluating, and launching profitable ecommerce products in the Indian market. Think Minea + PipiAds, optimized for India.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Project Goal

Build an **Agentic AI platform** that:

1. **Detects** trending products globally (TikTok, Amazon, AliExpress, Reddit, Facebook Ad Library, Google Trends)
2. **Evaluates** opportunity in the Indian market (Amazon IN, Flipkart, Meesho, D2C)
3. **Calculates** potential profitability (margin ≥ 40%)
4. **Generates** ad creatives and marketing angles
5. **Generates** Shopify product page content
6. **Displays** results in a React/Next.js dashboard

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         REACT / NEXT.JS DASHBOARD                        │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND                                │
│  REST API │ WebSockets │ Authentication │ Job Queues                     │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│  PostgreSQL     │    │  Redis (Cache/Queue)  │    │  Celery / Temporal   │
│  (Primary DB)   │    │  Session / Job State  │    │  (Agent Orchestration)│
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        AGENT PIPELINE (7 Agents)                         │
│  Trend → Market Gap → Supplier → Profit → Scoring → Creative → Shopify   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Option 1: Docker (Recommended)

```bash
# Clone and start all services
git clone <repo-url>
cd BharatProductIQ
docker compose up -d

# Access
# Dashboard: http://localhost:3000
# API:       http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Configure secrets
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Workers (separate terminal)
cd backend
celery -A app.workers.celery_app worker -l info
celery -A app.workers.celery_app beat -l info
```

---

## 📁 Repository Structure

```
BharatProductIQ/
├── agents/
│   ├── trend_agent/
│   ├── market_agent/
│   ├── supplier_agent/
│   ├── profit_agent/
│   ├── scoring_agent/
│   ├── creative_agent/
│   └── shopify_agent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── workers/
│   └── alembic/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   └── public/
├── docs/
├── docker/
└── scripts/
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md) | High-level system design & data flow |
| [AGENT_SPECIFICATIONS.md](docs/AGENT_SPECIFICATIONS.md) | Agent inputs, outputs, and logic |
| [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | Tables, relations, indexes |
| [API_SPEC.md](docs/API_SPEC.md) | REST API endpoints |
| [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) | Production deployment |
| [ROADMAP.md](docs/ROADMAP.md) | Feature roadmap & extensibility |

---

## 🔑 Environment Variables

```env
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/bharatproductiq
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
CELERY_BROKER_URL=redis://localhost:6379/1

# Optional (for data sources)
TIKTOK_SCRAPE_API_KEY=...
FACEBOOK_AD_LIBRARY_TOKEN=...
```

---

## 📊 Product Filters

The system **prioritizes** products with:

- ✅ **Strong visual demo potential** (TikTok/Reels-friendly)
- ✅ **Price range**: ₹799 – ₹2499
- ✅ **Margin**: ≥ 40%
- ✅ **Real problem-solving** (utility > novelty)

---

## 🔌 Extensibility

Planned / pluggable agents:

- Ad Spy Agent
- Competitor Store Analyzer
- Influencer Trend Detector
- Price Arbitrage Agent

---

## 📄 License

MIT
