"use client";

import { useEffect, useState } from "react";
import { ProductCard } from "@/components/ProductCard";
import { ProductDetailModal } from "@/components/ProductDetailModal";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";

interface TopProduct {
  id: string;
  product_name: string;
  trend_score: number | null;
  india_opportunity_score: number | null;
  estimated_margin_pct: number | null;
  total_score: number | null;
  supplier_link: string | null;
  product_images: string[];
}

export default function Home() {
  const [products, setProducts] = useState<TopProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/dashboard/top-opportunities?limit=10`)
      .then((r) => r.json())
      .then((d) => {
        setProducts(d.products || []);
      })
      .catch(() => setProducts([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen">
      <header className="bg-slate-900 text-white py-6 px-6 shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold tracking-tight">
            BharatProductIQ
          </h1>
          <span className="text-slate-400 text-sm">
            India-Focused Product Discovery
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-10">
        <section className="mb-10">
          <h2 className="text-xl font-semibold text-slate-800 mb-2">
            Top Opportunities
          </h2>
          <p className="text-slate-600 text-sm">
            AI-scored products with margin ≥40%, price ₹799–₹2499
          </p>
        </section>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-64 bg-slate-200 rounded-xl animate-pulse"
              />
            ))}
          </div>
        ) : products.length === 0 ? (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-8 text-center">
            <p className="text-amber-800 font-medium">No opportunities yet</p>
            <p className="text-amber-700 text-sm mt-1">
              Run the pipeline: POST /v1/pipeline/run
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((p) => (
              <ProductCard
                key={p.id}
                product={p}
                onClick={() => setSelectedId(p.id)}
              />
            ))}
          </div>
        )}

        {selectedId && (
          <ProductDetailModal
            productId={selectedId}
            onClose={() => setSelectedId(null)}
          />
        )}
      </main>
    </div>
  );
}
