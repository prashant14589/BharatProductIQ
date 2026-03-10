"""Celery application for BharatProductIQ."""

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "bharatproductiq",
    broker=settings.celery_broker_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    beat_schedule={
        "run-pipeline-every-12h": {
            "task": "app.workers.tasks.run_pipeline_task",
            "schedule": crontab(hour="*/12", minute=0),
        },
    },
)
