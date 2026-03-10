# Roadmap — BharatProductIQ

## Phase 1: MVP (Current)

- [x] Agent specifications and architecture
- [ ] Trend Detection Agent (TikTok, Amazon US, AliExpress, Google Trends)
- [ ] Market Gap Agent (Amazon IN, Flipkart)
- [ ] Supplier Discovery Agent (AliExpress, CJ)
- [ ] Profitability + Scoring + Creative + Shopify agents
- [ ] FastAPI backend with CRUD + pipeline trigger
- [ ] Next.js dashboard with product cards + detail modal
- [ ] Celery pipeline orchestration
- [ ] 12h scheduled scans

---

## Phase 2: Data Quality & Scale

- [ ] Reddit, Facebook Ad Library integration
- [ ] Meesho, 1688, Alibaba suppliers
- [ ] Caching layer (Redis) for API responses
- [ ] Retry and rate-limit handling for external APIs
- [ ] Image storage (S3) for product images

---

## Phase 3: SaaS Features

- [ ] User authentication (JWT)
- [ ] Multi-tenant data isolation
- [ ] Saved products / favorites
- [ ] Email alerts for new top opportunities
- [ ] Subscription tiers (free, pro, enterprise)

---

## Phase 4: Extensibility

- [ ] **Ad Spy Agent**: Pull competitor creatives from Meta/TikTok
- [ ] **Competitor Store Analyzer**: Analyze Shopify/Woo stores
- [ ] **Influencer Trend Detector**: Track influencer promotions
- [ ] **Price Arbitrage Agent**: Cross-platform price comparison
- [ ] Plugin/agent registry for custom agents

---

## Phase 5: Intelligence

- [ ] Visual similarity search (product images)
- [ ] Seasonal trend forecasting
- [ ] Automated A/B test suggestions for ad copy
- [ ] Competitor price monitoring
