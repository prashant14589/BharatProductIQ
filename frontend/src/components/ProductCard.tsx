"use client";

interface ProductCardProps {
  product: {
    id: string;
    product_name: string;
    trend_score: number | null;
    india_opportunity_score: number | null;
    estimated_margin_pct: number | null;
    total_score: number | null;
    supplier_link: string | null;
    product_images: string[];
  };
  onClick: () => void;
}

export function ProductCard({ product, onClick }: ProductCardProps) {
  const img = product.product_images?.[0] || "https://via.placeholder.com/400x400?text=No+Image";

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => e.key === "Enter" && onClick()}
      className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md hover:border-brand-500/30 transition-all cursor-pointer"
    >
      <div className="aspect-square bg-slate-100 relative">
        <img
          src={img}
          alt={product.product_name}
          className="w-full h-full object-cover"
        />
        {product.total_score != null && (
          <span className="absolute top-2 right-2 bg-brand-600 text-white text-xs font-bold px-2 py-1 rounded">
            {product.total_score}
          </span>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-slate-800 line-clamp-2">
          {product.product_name}
        </h3>
        <div className="flex gap-4 mt-3 text-sm text-slate-600">
          {product.trend_score != null && (
            <span>Trend: {product.trend_score}</span>
          )}
          {product.india_opportunity_score != null && (
            <span>India: {product.india_opportunity_score}</span>
          )}
          {product.estimated_margin_pct != null && (
            <span className="text-brand-600 font-medium">
              Margin: {product.estimated_margin_pct.toFixed(0)}%
            </span>
          )}
        </div>
        {product.supplier_link && (
          <a
            href={product.supplier_link}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="text-xs text-brand-600 hover:underline mt-2 inline-block"
          >
            Supplier link →
          </a>
        )}
      </div>
    </div>
  );
}
