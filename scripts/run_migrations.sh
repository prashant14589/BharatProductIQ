#!/bin/bash
# Run database migrations
cd "$(dirname "$0")/.."
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/bharatproductiq}"
cd backend && alembic upgrade head
