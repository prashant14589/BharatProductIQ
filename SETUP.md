# BharatProductIQ — Setup Instructions

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+**
- **Redis 7+**
- **Docker & Docker Compose** (optional)

---

## Option 1: Docker Compose (Fastest)

```bash
# 1. Clone and enter project
cd BharatProductIQ

# 2. Start services
docker compose up -d

# 3. Run migrations (first time only)
docker compose exec backend alembic upgrade head

# 4. (Optional) Trigger pipeline to populate data
curl -X POST http://localhost:8000/v1/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"limit_trends": 5, "top_n": 5}'

# Access
# - Dashboard: http://localhost:3000
# - API:       http://localhost:8000
# - API Docs:  http://localhost:8000/docs
```

---

## Option 2: Local Development

### Backend

```bash
cd backend

# Create virtual env
python -m venv venv
# Windows: venv\Scripts\activate
# Unix:    source venv/bin/activate

# Install
pip install -r requirements.txt

# Copy env
cp .env.example .env
# Edit .env: set DATABASE_URL, REDIS_URL, OPENAI_API_KEY or ANTHROPIC_API_KEY

# Migrations (ensure PostgreSQL is running)
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bharatproductiq
alembic upgrade head

# Run server
uvicorn app.main:app --reload --port 8000
```

### Celery Workers (Separate Terminals)

```bash
cd backend
celery -A app.workers.celery_app worker -l info
celery -A app.workers.celery_app beat -l info
```

### Frontend

```bash
cd frontend

npm install
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000/v1

npm run dev
```

### Populate Data

```bash
# From project root
cd backend
python -c "
from app.core.database import SessionLocal
from app.services.pipeline import run_pipeline
db = SessionLocal()
run_pipeline(db, limit_trends=5, top_n=5)
db.close()
"
# Or: curl -X POST http://localhost:8000/v1/pipeline/run -H "Content-Type: application/json" -d '{"limit_trends":5,"top_n":5}'
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| REDIS_URL | Yes | Redis URL |
| CELERY_BROKER_URL | Yes | Same as REDIS_URL or separate Redis DB |
| OPENAI_API_KEY | For AI | OpenAI API key (Creative/Shopify agents) |
| ANTHROPIC_API_KEY | For AI | Anthropic API key (alternative) |

---

## Verification

1. **Health**: `curl http://localhost:8000/health`
2. **API Docs**: Open http://localhost:8000/docs
3. **Dashboard**: Open http://localhost:3000 — should show "No opportunities yet" until pipeline runs
4. **Run pipeline**: POST `/v1/pipeline/run` then refresh dashboard
