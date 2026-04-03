"""Product API routes."""

from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from fastapi import APIRouter, Depends, Query
from app.core.database import get_db
from app.models import Product, ProductSupplier, Supplier
from app.schemas.product import ProductListItem, ProductDetail, ProductListResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    status: str | None = Query(None),
    min_score: int | None = Query(None, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    from app.models import ProductScore
    q = db.query(Product).filter(Product.status == (status or "scored"))
    if min_score is not None:
        q = q.join(ProductScore).filter(ProductScore.total_score >= min_score)
    total = q.count()
    products = (
        q.options(
            joinedload(Product.trend_signal),
            joinedload(Product.market_gap),
            joinedload(Product.profit_model),
            joinedload(Product.product_score),
            joinedload(Product.product_suppliers).joinedload(ProductSupplier.supplier),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    items = []
    for p in products:
        ps = p.product_score
        supplier_link = None
        if p.product_suppliers:
            for ps_rel in p.product_suppliers:
                if (
                    ps_rel.is_primary
                    and ps_rel.supplier
                    and ps_rel.supplier.supplier_url
                ):
                    supplier_link = ps_rel.supplier.supplier_url
                    break
            if supplier_link is None:
                for ps_rel in p.product_suppliers:
                    if ps_rel.supplier and ps_rel.supplier.supplier_url:
                        supplier_link = ps_rel.supplier.supplier_url
                        break
        items.append(
            ProductListItem(
                id=p.id,
                product_name=p.product_name,
                category=p.category,
                status=p.status,
                trend_score=p.trend_signal.trend_score if p.trend_signal else None,
                india_opportunity_score=p.market_gap.opportunity_score if p.market_gap else None,
                estimated_margin_pct=p.profit_model.estimated_margin_pct if p.profit_model else None,
                total_score=ps.total_score if ps else None,
                supplier_link=supplier_link,
                product_images=p.product_images or [],
            )
        )
    return ProductListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    p = (
        db.query(Product)
        .options(
            joinedload(Product.trend_signal),
            joinedload(Product.market_gap),
            joinedload(Product.profit_model),
            joinedload(Product.product_score),
            joinedload(Product.ad_creative),
            joinedload(Product.shopify_page),
            joinedload(Product.product_suppliers).joinedload(ProductSupplier.supplier),
        )
        .filter(Product.id == product_id)
        .first()
    )
    if not p:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")

    def to_dict(obj, exclude=None):
        if obj is None:
            return None
        d = {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
        for k, v in d.items():
            if hasattr(v, "quantize"):
                d[k] = float(v)
        return d

    suppliers = []
    for ps in p.product_suppliers or []:
        if ps.supplier:
            s = ps.supplier
            suppliers.append({
                "supplier_name": s.supplier_name,
                "supplier_url": s.supplier_url,
                "unit_cost_inr": float(s.unit_cost_inr) if s.unit_cost_inr else None,
                "shipping_cost_inr": float(s.shipping_cost_inr) if s.shipping_cost_inr else None,
                "moq": s.moq,
                "white_label_available": s.white_label_available,
            })

    return ProductDetail(
        id=p.id,
        product_name=p.product_name,
        category=p.category,
        product_images=p.product_images or [],
        video_links=p.video_links or [],
        status=p.status,
        created_at=p.created_at,
        updated_at=p.updated_at,
        trend_signals=to_dict(p.trend_signal) if p.trend_signal else None,
        market_gap=to_dict(p.market_gap) if p.market_gap else None,
        suppliers=suppliers,
        profit_model=to_dict(p.profit_model) if p.profit_model else None,
        product_score=to_dict(p.product_score) if p.product_score else None,
        ad_creatives=to_dict(p.ad_creative) if p.ad_creative else None,
        shopify_page=to_dict(p.shopify_page) if p.shopify_page else None,
    )
