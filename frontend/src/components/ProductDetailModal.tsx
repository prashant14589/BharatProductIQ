"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";

interface ProductDetailModalProps {
  productId: string;
  onClose: () => void;
}

export function ProductDetailModal({ productId, onClose }: ProductDetailModalProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/products/${productId}`)
      .then((r) => r.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, [productId]);

  if (loading || !data) {
    return (
      <div
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        onClick={onClose}
      >
        <div className="bg-white rounded-xl p-8 max-w-lg" onClick={(e) => e.stopPropagation()}>
          Loading...
        </div>
      </div>
    );
  }

  const profit = data.profit_model;
  const creatives = data.ad_creatives;
  const shopify = data.shopify_page;

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-semibold">{data.product_name}</h2>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-700 text-2xl leading-none"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6">
          {data.product_images?.length > 0 && (
            <div className="flex gap-2 overflow-x-auto pb-2">
              {data.product_images.map((url: string, i: number) => (
                <img
                  key={i}
                  src={url}
                  alt=""
                  className="w-32 h-32 object-cover rounded-lg flex-shrink-0"
                />
              ))}
            </div>
          )}

          {profit && (
            <section>
              <h3 className="font-semibold text-slate-800 mb-2">Profit Breakdown</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span className="text-slate-600">Total Cost</span>
                <span>₹{profit.total_cost_inr}</span>
                <span className="text-slate-600">Suggested Price</span>
                <span className="text-brand-600 font-medium">₹{profit.suggested_price_inr}</span>
                <span className="text-slate-600">Margin</span>
                <span className="text-brand-600 font-medium">{profit.estimated_margin_pct}%</span>
              </div>
            </section>
          )}

          {data.suppliers?.length > 0 && (
            <section>
              <h3 className="font-semibold text-slate-800 mb-2">Supplier Info</h3>
              {data.suppliers.map((s: any, i: number) => (
                <div key={i} className="text-sm space-y-1">
                  {s.supplier_url && (
                    <a
                      href={s.supplier_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-brand-600 hover:underline"
                    >
                      {s.supplier_name || "Supplier"} →
                    </a>
                  )}
                  <p>Unit cost: ₹{s.unit_cost_inr}, Shipping: ₹{s.shipping_cost_inr}, MOQ: {s.moq}</p>
                </div>
              ))}
            </section>
          )}

          {creatives?.ad_hooks?.length > 0 && (
            <section>
              <h3 className="font-semibold text-slate-800 mb-2">Ad Hooks</h3>
              <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
                {creatives.ad_hooks.map((h: string, i: number) => (
                  <li key={i}>{h}</li>
                ))}
              </ul>
            </section>
          )}

          {creatives?.short_form_scripts?.length > 0 && (
            <section>
              <h3 className="font-semibold text-slate-800 mb-2">Video Script</h3>
              <p className="text-sm text-slate-700 whitespace-pre-wrap">
                {creatives.short_form_scripts[0]?.script}
              </p>
            </section>
          )}

          {shopify?.product_description && (
            <section>
              <h3 className="font-semibold text-slate-800 mb-2">Shopify Description</h3>
              <p className="text-sm text-slate-700">{shopify.product_description}</p>
              {shopify.benefit_bullets?.length > 0 && (
                <ul className="mt-2 list-disc list-inside text-sm text-slate-700 space-y-1">
                  {shopify.benefit_bullets.map((b: string, i: number) => (
                    <li key={i}>{b}</li>
                  ))}
                </ul>
              )}
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
