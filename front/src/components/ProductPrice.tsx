function formatPrice(kopecks: number, currency: string): string {
  const value = kopecks / 100;
  try {
    return new Intl.NumberFormat("ru-RU", {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(value);
  } catch {
    return `${value} ${currency}`;
  }
}

export function productHasSale(product: {
  sale_discount_percent?: number | null;
  sale_unit_price?: number | null;
}): boolean {
  return (
    product.sale_discount_percent != null &&
    product.sale_discount_percent > 0 &&
    product.sale_unit_price != null
  );
}

export function ProductPrice({
  unitPrice,
  currency,
  saleUnitPrice,
  saleDiscountPercent,
  className = "",
  align = "end",
}: {
  unitPrice: number;
  currency: string;
  saleUnitPrice?: number | null;
  saleDiscountPercent?: number | null;
  className?: string;
  align?: "start" | "end";
}) {
  const onSale =
    saleDiscountPercent != null &&
    saleDiscountPercent > 0 &&
    saleUnitPrice != null;
  const alignClass = align === "end" ? "items-end text-right" : "items-start text-left";

  if (!onSale) {
    return (
      <p className={`product-price font-semibold tabular-nums text-white ${className}`}>
        {formatPrice(unitPrice, currency)}
      </p>
    );
  }

  return (
    <div className={`product-price flex flex-col gap-1 ${alignClass} ${className}`}>
      <span className="sale-badge">−{saleDiscountPercent}%</span>
      <div className="flex flex-wrap items-baseline justify-end gap-2">
        <span className="text-sm tabular-nums text-slate-500 line-through">
          {formatPrice(unitPrice, currency)}
        </span>
        <span className="font-semibold tabular-nums text-emerald-300">
          {formatPrice(saleUnitPrice, currency)}
        </span>
      </div>
    </div>
  );
}

export { formatPrice };
