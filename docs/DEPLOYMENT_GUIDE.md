# Deployment Guide — BharatProductIQ

## 1. Overview

Deployment targets: Docker Compose (staging), cloud (production). This guide covers both.

---

## 2. Docker Compose (Staging / Local Prod)

### Structure

```
docker/
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── .env.docker
```

### Commands

```bash
# Build and start
docker compose up -d --build

# View logs
docker compose logs -f backend

# Run migrations
docker compose exec backend alembic upgrade head

# Stop
docker compose down
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| backend | 8000 | FastAPI app |
| frontend | 3000 | Next.js app |
| postgres | 5432 | PostgreSQL |
| redis | 6379 | Redis |
| celery_worker | - | Celery worker |
| celery_beat | - | Celery beat scheduler |

---

## 3. Production (Cloud)

### Recommended Stack

- **Compute**: AWS ECS / GCP Cloud Run / Railway
- **Database**: AWS RDS PostgreSQL / Supabase / Neon
- **Cache**: AWS ElastiCache Redis / Upstash
- **Object Storage**: S3 (for product images, if stored)

### Environment Variables

```env
# Required
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
CELERY_BROKER_URL=redis://host:6379/1
OPENAI_API_KEY=sk-...
# or ANTHROPIC_API_KEY=sk-ant-...

# Optional
FRONTEND_URL=https://app.bharatproductiq.com
CORS_ORIGINS=https://app.bharatproductiq.com
LOG_LEVEL=info
SENTRY_DSN=https://...
```

### Celery Workers

Run 2–4 worker processes depending on load:

```bash
celery -A app.workers.celery_app worker -l info -c 4
celery -A app.workers.celery_app beat -l info
```

### Cron / Scheduler

If not using Celery Beat, use system cron:

```cron
0 */12 * * * curl -X POST https://api.bharatproductiq.com/v1/pipeline/run -H "Authorization: Bearer $INTERNAL_TOKEN"
```

---

## 4. Database Migrations

```bash
# Create migration
alembic revision -m "add_shopify_pages"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 5. Health Checks

- `/health` — API + DB + Redis connectivity
- Celery: `celery -A app.workers.celery_app inspect ping`

---

## 6. Monitoring

- **Logs**: Structured JSON logs to stdout (captured by cloud log aggregation)
- **Metrics**: Prometheus `/metrics` (optional)
- **Errors**: Sentry for exception tracking
- **Uptime**: External ping to `/health` every 5 min

---

## 7. Security Checklist

- [ ] All secrets in env / secrets manager
- [ ] HTTPS only
- [ ] CORS restricted to frontend origin
- [ ] Rate limiting on API
- [ ] Database credentials rotated
- [ ] Redis not exposed to public
