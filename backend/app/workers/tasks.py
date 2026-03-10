"""Celery tasks for pipeline execution."""

from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.pipeline import run_pipeline


@celery_app.task(bind=True)
def run_pipeline_task(self, limit_trends: int = 50, top_n: int = 5):
    """Run pipeline asynchronously. Called by Celery Beat every 12h."""
    db = SessionLocal()
    try:
        run_id = run_pipeline(db, limit_trends=limit_trends, top_n=top_n)
        return {"pipeline_run_id": str(run_id), "status": "completed"}
    finally:
        db.close()
