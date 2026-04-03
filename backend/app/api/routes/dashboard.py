"""Dashboard API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Product, ProductScore, ProductSupplier, Supplier

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/top-opportunities")
def top_opportunities(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Top N scored products for dashboard. Consider caching in Redis."""
    q = (
        db.query(Product)
        .join(ProductScore)
        .filter(Product.status == "scored")
        .order_by(ProductScore.total_score.desc(), Product.updated_at.desc())
    )
    ranked_products = q.all()
    products = []
    seen_names: set[str] = set()
    for p in ranked_products:
        key = (p.product_name or "").strip().lower()
        if key in seen_names:
            continue
        seen_names.add(key)
        products.append(p)
        if len(products) >= limit:
            break
    items = []
    for p in products:
        supplier_link = None
        for ps in p.product_suppliers or []:
            if ps.is_primary and ps.supplier and ps.supplier.supplier_url:
                supplier_link = ps.supplier.supplier_url
                break
        if supplier_link is None:
            for ps in p.product_suppliers or []:
                if ps.supplier and ps.supplier.supplier_url:
                    supplier_link = ps.supplier.supplier_url
                    break
        items.append({
            "id": str(p.id),
            "product_name": p.product_name,
            "trend_score": p.trend_signal.trend_score if p.trend_signal else None,
            "india_opportunity_score": p.market_gap.opportunity_score if p.market_gap else None,
            "estimated_margin_pct": float(p.profit_model.estimated_margin_pct) if p.profit_model else None,
            "total_score": p.product_score.total_score if p.product_score else None,
            "supplier_link": supplier_link,
            "product_images": p.product_images or [],
        })
    return {
        "products": items,
        "cached_at": None,  # Set when Redis cache is used
    }
