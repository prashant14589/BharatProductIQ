"""Pipeline API routes."""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models import PipelineRun, Product, ProductScore
from app.services.pipeline import run_pipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


class PipelineRunRequest(BaseModel):
    limit_trends: int = 50
    top_n: int = 5


@router.post("/run")
def trigger_pipeline(
    body: PipelineRunRequest | None = None,
    db: Session = Depends(get_db),
):
    body = body or PipelineRunRequest()
    run_id = run_pipeline(
        db,
        limit_trends=body.limit_trends,
        top_n=body.top_n,
    )
    return {
        "pipeline_run_id": str(run_id),
        "status": "running",
        "message": f"Pipeline started. Check /pipeline/runs/{run_id} for progress.",
    }


@router.get("/runs")
def list_runs(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(PipelineRun).order_by(PipelineRun.started_at.desc())
    total = q.count()
    runs = q.offset(offset).limit(limit).all()
    return {
        "items": [
            {
                "id": str(r.id),
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "status": r.status,
                "products_discovered": r.products_discovered,
                "products_scored": r.products_scored,
                "top_products_count": r.top_products_count,
            }
            for r in runs
        ],
        "total": total,
    }


@router.get("/runs/{run_id}")
def get_run(run_id: UUID, db: Session = Depends(get_db)):
    r = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
    if not r:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    # Top product IDs by score
    top = (
        db.query(Product.id)
        .join(ProductScore)
        .filter(Product.pipeline_run_id == run_id, Product.status == "scored")
        .order_by(ProductScore.total_score.desc())
        .limit(r.top_products_count or 5)
        .all()
    )
    return {
        "id": str(r.id),
        "started_at": r.started_at.isoformat() if r.started_at else None,
        "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        "status": r.status,
        "products_discovered": r.products_discovered,
        "products_scored": r.products_scored,
        "top_products_count": r.top_products_count,
        "top_product_ids": [str(p.id) for p in top],
    }
