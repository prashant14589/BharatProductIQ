"""Pipeline orchestration - runs agents in sequence and persists to DB."""

import os
import sys
import uuid
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

from app.services.canonicalization import canonical_product_key
from app.services.image_scoring import estimate_visual_demo_potential


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
            category = t.get("category")
            ext_id = t.get("external_id") or canonical_product_key(t["product_name"], category)

            product = db.query(Product).filter(Product.external_id == ext_id).first()
            if not product:
                product = Product(
                    external_id=ext_id,
                    product_name=t["product_name"],
                    category=category,
                    product_images=t.get("product_images", []),
                    video_links=t.get("video_links", []),
                    status="processing",
                    pipeline_run_id=run_id,
                )
                db.add(product)
                db.flush()
            else:
                product.product_name = t["product_name"]
                product.category = category
                product.product_images = t.get("product_images", [])
                product.video_links = t.get("video_links", [])
                product.status = "processing"
                product.pipeline_run_id = run_id

            ts = db.query(TrendSignal).filter(TrendSignal.product_id == product.id).first()
            if not ts:
                ts = TrendSignal(
                    product_id=product.id,
                    trend_score=t.get("trend_score", 0),
                    trend_sources=t.get("trend_sources", []),
                    raw_signals=t,
                )
                db.add(ts)
            else:
                ts.trend_score = t.get("trend_score", 0)
                ts.trend_sources = t.get("trend_sources", [])
                ts.raw_signals = t

            ctx = {
                "product_name": product.product_name,
                "category": product.category,
                "trend_score": t.get("trend_score", 0),
                "product_images": product.product_images,
            }
            ctx["visual_demo_potential"] = estimate_visual_demo_potential(
                product.product_name, product.category, product.product_images
            )

            # Market Gap
            market_agent = get_agent("market_gap")
            mg_out = market_agent.run(ctx)
            mg = db.query(MarketGap).filter(MarketGap.product_id == product.id).first()
            if not mg:
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
            else:
                mg.india_saturation_score = mg_out["india_saturation_score"]
                mg.competitor_count = mg_out["competitor_count"]
                mg.average_price_inr = mg_out["average_price_inr"]
                mg.brand_presence = mg_out["brand_presence"]
                mg.opportunity_score = mg_out["opportunity_score"]
                mg.top_competitors = mg_out.get("top_competitors", [])
            ctx.update(mg_out)

            # Supplier
            supplier_agent = get_agent("supplier")
            sup_out = supplier_agent.run(ctx)

            supplier_candidates = sup_out.get("supplier_candidates") or []
            # Choose best candidate when available; otherwise fall back to supplier_links[0]
            if supplier_candidates:
                supplier_candidates.sort(
                    key=lambda c: float(c.get("match_confidence") or 0), reverse=True
                )
                ctx["supplier_match_confidence"] = supplier_candidates[0].get(
                    "match_confidence"
                )
            else:
                ctx["supplier_match_confidence"] = None
                supplier_candidates = [
                    {
                        "supplier_name": "Primary Supplier",
                        "platform": "aliexpress",
                        "supplier_url": sup_out["supplier_links"][0]
                        if sup_out.get("supplier_links")
                        else "",
                        "match_confidence": 0.6,
                    }
                ]

            # Persist top supplier candidates (up to 3) and link them to this product.
            top_candidates = supplier_candidates[:3]

            # Replace previous supplier links for this product
            db.query(ProductSupplier).filter(
                ProductSupplier.product_id == product.id
            ).delete()

            for i, c in enumerate(top_candidates):
                supplier_url = c.get("supplier_url") or ""
                if not supplier_url:
                    continue

                supplier = (
                    db.query(Supplier).filter(Supplier.supplier_url == supplier_url).first()
                )
                if not supplier:
                    supplier = Supplier(
                        supplier_name=c.get("supplier_name")
                        or f"{product.product_name} Supplier",
                        supplier_url=supplier_url,
                        platform=c.get("platform") or "aliexpress",
                        unit_cost_usd=sup_out["unit_cost_usd"],
                        unit_cost_inr=sup_out["unit_cost_inr"],
                        shipping_cost_inr=sup_out["shipping_cost_inr"],
                        moq=sup_out["moq"],
                        white_label_available=sup_out["white_label_available"],
                        lead_time_days=sup_out.get("lead_time_days", 14),
                    )
                    db.add(supplier)
                    db.flush()
                else:
                    # Keep Supplier record up to date with current estimate
                    supplier.supplier_name = c.get("supplier_name") or supplier.supplier_name
                    supplier.platform = c.get("platform") or supplier.platform
                    supplier.unit_cost_usd = sup_out["unit_cost_usd"]
                    supplier.unit_cost_inr = sup_out["unit_cost_inr"]
                    supplier.shipping_cost_inr = sup_out["shipping_cost_inr"]
                    supplier.moq = sup_out["moq"]
                    supplier.white_label_available = sup_out["white_label_available"]
                    supplier.lead_time_days = sup_out.get("lead_time_days", supplier.lead_time_days)

                db.add(
                    ProductSupplier(
                        product_id=product.id,
                        supplier_id=supplier.id,
                        is_primary=(i == 0),
                    )
                )

            ctx.update(sup_out)

            # Profit
            profit_agent = get_agent("profit")
            pm_out = profit_agent.run(ctx)
            if pm_out is None:
                product.status = "rejected"
                continue
            pm = db.query(ProfitModel).filter(ProfitModel.product_id == product.id).first()
            if not pm:
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
            else:
                pm.unit_cost_inr = pm_out["unit_cost_inr"]
                pm.shipping_cost_inr = pm_out["shipping_cost_inr"]
                pm.ad_cost_per_unit_inr = pm_out["ad_cost_per_unit_inr"]
                pm.total_cost_inr = pm_out["total_cost_inr"]
                pm.suggested_price_inr = pm_out["suggested_price_inr"]
                pm.estimated_margin_pct = pm_out["estimated_margin_pct"]
                pm.price_in_range = pm_out["price_in_range"]
            ctx.update(pm_out)

            # Scoring
            scoring_agent = get_agent("scoring")
            sc_out = scoring_agent.run(ctx)
            if sc_out is None:
                product.status = "rejected"
                continue

            ps_model = db.query(ProductScore).filter(ProductScore.product_id == product.id).first()
            if not ps_model:
                ps_model = ProductScore(
                    product_id=product.id,
                    total_score=sc_out["total_score"],
                    score_breakdown=sc_out["score_breakdown"],
                )
                db.add(ps_model)
            else:
                ps_model.total_score = sc_out["total_score"]
                ps_model.score_breakdown = sc_out["score_breakdown"]
            ctx.update(sc_out)
            product.status = "scored"
            scored_ids.append((product.id, sc_out["total_score"]))

            # Creative
            creative_agent = get_agent("creative")
            cr_out = creative_agent.run(ctx)
            ac = db.query(AdCreative).filter(AdCreative.product_id == product.id).first()
            if not ac:
                ac = AdCreative(
                    product_id=product.id,
                    ad_hooks=cr_out.get("ad_hooks", []),
                    short_form_scripts=cr_out.get("short_form_scripts", []),
                    marketing_angles=cr_out.get("marketing_angles", []),
                    meta_targeting=cr_out.get("meta_targeting", {}),
                )
                db.add(ac)
            else:
                ac.ad_hooks = cr_out.get("ad_hooks", [])
                ac.short_form_scripts = cr_out.get("short_form_scripts", [])
                ac.marketing_angles = cr_out.get("marketing_angles", [])
                ac.meta_targeting = cr_out.get("meta_targeting", {})

            # Shopify
            shopify_agent = get_agent("shopify")
            sh_out = shopify_agent.run(ctx)
            sp = db.query(ShopifyPage).filter(ShopifyPage.product_id == product.id).first()
            if not sp:
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
            else:
                sp.product_title = sh_out.get("product_title", "")
                sp.product_description = sh_out.get("product_description", "")
                sp.benefit_bullets = sh_out.get("benefit_bullets", [])
                sp.faqs = sh_out.get("faqs", [])
                sp.upsell_suggestions = sh_out.get("upsell_suggestions", [])
                sp.meta_title = sh_out.get("meta_title", "")
                sp.meta_description = sh_out.get("meta_description", "")

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
