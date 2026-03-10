"""Pipeline orchestration - runs agents in sequence and persists to DB."""

import os
import sys
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session

# Add project root for agent imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from agents.registry import get_agent
from app.models import (
    Product,
    TrendSignal,
    MarketGap,
    Supplier,
    ProductSupplier,
    ProfitModel,
    ProductScore,
    AdCreative,
    ShopifyPage,
    PipelineRun,
)


def run_pipeline(db: Session, limit_trends: int = 50, top_n: int = 5) -> uuid.UUID:
    """
    Execute full pipeline: Trend -> Market -> Supplier -> Profit -> Score -> Creative -> Shopify.
    Persist all data and return pipeline_run_id.
    """
    run = PipelineRun(status="running", top_products_count=top_n)
    db.add(run)
    db.commit()
    run_id = run.id

    try:
        trend_agent = get_agent("trend")
        trends = trend_agent.run({"keywords": []})
        trends = trends[:limit_trends]
        run.products_discovered = len(trends)

        scored_ids = []
        for t in trends:
            product = Product(
                external_id=f"trend_{uuid.uuid4().hex[:12]}",
                product_name=t["product_name"],
                category=t.get("category"),
                product_images=t.get("product_images", []),
                video_links=t.get("video_links", []),
                status="processing",
                pipeline_run_id=run_id,
            )
            db.add(product)
            db.flush()

            ts = TrendSignal(
                product_id=product.id,
                trend_score=t.get("trend_score", 0),
                trend_sources=t.get("trend_sources", []),
                raw_signals=t,
            )
            db.add(ts)

            ctx = {
                "product_name": product.product_name,
                "category": product.category,
                "trend_score": t.get("trend_score", 0),
                "product_images": product.product_images,
            }

            # Market Gap
            market_agent = get_agent("market_gap")
            mg_out = market_agent.run(ctx)
            mg = MarketGap(
                product_id=product.id,
                india_saturation_score=mg_out["india_saturation_score"],
                competitor_count=mg_out["competitor_count"],
                average_price_inr=mg_out["average_price_inr"],
                brand_presence=mg_out["brand_presence"],
                opportunity_score=mg_out["opportunity_score"],
                top_competitors=mg_out.get("top_competitors", []),
            )
            db.add(mg)
            ctx.update(mg_out)

            # Supplier
            supplier_agent = get_agent("supplier")
            sup_out = supplier_agent.run(ctx)
            supplier = Supplier(
                supplier_name="Primary Supplier",
                supplier_url=sup_out["supplier_links"][0] if sup_out["supplier_links"] else "",
                platform="aliexpress",
                unit_cost_usd=sup_out["unit_cost_usd"],
                unit_cost_inr=sup_out["unit_cost_inr"],
                shipping_cost_inr=sup_out["shipping_cost_inr"],
                moq=sup_out["moq"],
                white_label_available=sup_out["white_label_available"],
                lead_time_days=sup_out.get("lead_time_days", 14),
            )
            db.add(supplier)
            db.flush()
            ps = ProductSupplier(product_id=product.id, supplier_id=supplier.id, is_primary=True)
            db.add(ps)
            ctx.update(sup_out)

            # Profit
            profit_agent = get_agent("profit")
            pm_out = profit_agent.run(ctx)
            if pm_out is None:
                product.status = "rejected"
                continue
            pm = ProfitModel(
                product_id=product.id,
                unit_cost_inr=pm_out["unit_cost_inr"],
                shipping_cost_inr=pm_out["shipping_cost_inr"],
                ad_cost_per_unit_inr=pm_out["ad_cost_per_unit_inr"],
                total_cost_inr=pm_out["total_cost_inr"],
                suggested_price_inr=pm_out["suggested_price_inr"],
                estimated_margin_pct=pm_out["estimated_margin_pct"],
                price_in_range=pm_out["price_in_range"],
            )
            db.add(pm)
            ctx.update(pm_out)

            # Scoring
            scoring_agent = get_agent("scoring")
            sc_out = scoring_agent.run(ctx)
            if sc_out is None:
                product.status = "rejected"
                continue

            ps_model = ProductScore(
                product_id=product.id,
                total_score=sc_out["total_score"],
                score_breakdown=sc_out["score_breakdown"],
            )
            db.add(ps_model)
            ctx.update(sc_out)
            product.status = "scored"
            scored_ids.append((product.id, sc_out["total_score"]))

            # Creative
            creative_agent = get_agent("creative")
            cr_out = creative_agent.run(ctx)
            ac = AdCreative(
                product_id=product.id,
                ad_hooks=cr_out.get("ad_hooks", []),
                short_form_scripts=cr_out.get("short_form_scripts", []),
                marketing_angles=cr_out.get("marketing_angles", []),
                meta_targeting=cr_out.get("meta_targeting", {}),
            )
            db.add(ac)

            # Shopify
            shopify_agent = get_agent("shopify")
            sh_out = shopify_agent.run(ctx)
            sp = ShopifyPage(
                product_id=product.id,
                product_title=sh_out.get("product_title", ""),
                product_description=sh_out.get("product_description", ""),
                benefit_bullets=sh_out.get("benefit_bullets", []),
                faqs=sh_out.get("faqs", []),
                upsell_suggestions=sh_out.get("upsell_suggestions", []),
                meta_title=sh_out.get("meta_title", ""),
                meta_description=sh_out.get("meta_description", ""),
            )
            db.add(sp)

        run.products_scored = len(scored_ids)
        scored_ids.sort(key=lambda x: x[1], reverse=True)
        from datetime import datetime, timezone
        run.completed_at = datetime.now(timezone.utc)
        run.status = "completed"
        db.commit()
        return run_id

    except Exception as e:
        run.status = "failed"
        run.error_message = str(e)
        db.commit()
        raise
