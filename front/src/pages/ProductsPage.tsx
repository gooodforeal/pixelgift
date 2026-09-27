import { useState, type MouseEvent, type ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ChevronLeft,
  ChevronRight,
  Gift,
  LayoutGrid,
  List,
  Package,
  Plus,
} from "lucide-react";

import { PageTransition } from "../components/PageTransition";
import { ProductPrice } from "../components/ProductPrice";
import { Spinner } from "../components/Spinner";
import { useAuth } from "../hooks/useAuth";
import { ApiError, api, toProxiedAssetUrl } from "../lib/api";
import type { Cart, Product } from "../lib/types";

type ProductsView = "grid" | "list";

const PRODUCTS_VIEW_STORAGE_KEY = "pixelgift.products-view";

function resolveInitialProductsView(): ProductsView {
  if (typeof window === "undefined") return "grid";
  const stored = window.localStorage.getItem(PRODUCTS_VIEW_STORAGE_KEY);
  return stored === "list" || stored === "grid" ? stored : "grid";
}

function ProductThumb({
  urls,
  name,
  fallback,
  className = "h-16 w-16 sm:h-[4.5rem] sm:w-28",
}: {
  urls: string[];
  name: string;
  fallback: "gift" | "package";
  className?: string;
}) {
  if (!urls.length) {
    const Icon = fallback === "gift" ? Gift : Package;
    return (
      <div
        className={`flex items-center justify-center bg-gradient-to-br from-glow-cyan/10 via-transparent to-glow-violet/10 ${className}`}
      >
        <Icon
          className={`size-7 ${
            fallback === "gift" ? "text-glow-cyan/80" : "text-slate-500/70"
          }`}
          strokeWidth={1.5}
        />
      </div>
    );
  }
  return (
    <img
      src={toProxiedAssetUrl(urls[0]!)}
      alt={name}
      className={`object-cover ${className}`}
      loading="lazy"
    />
  );
}

function ProductGallery({
  urls,
  name,
  fallback,
  openHref,
}: {
  urls: string[];
  name: string;
  fallback: "gift" | "package";
  openHref: string;
}) {
  const [index, setIndex] = useState(0);
  const stop = (event: MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
  };

  let media: ReactNode;
  if (!urls.length) {
    const Icon = fallback === "gift" ? Gift : Package;
    media = (
      <div className="flex h-44 items-center justify-center bg-gradient-to-br from-glow-cyan/15 via-ink-950/30 to-glow-violet/15">
        <Icon
          className={`size-12 ${
            fallback === "gift" ? "text-glow-cyan/80" : "text-slate-500/70"
          }`}
          strokeWidth={1.5}
        />
      </div>
    );
  } else {
    const current = toProxiedAssetUrl(urls[index] ?? urls[0]!);
    media = (
      <div className="relative h-44 overflow-hidden bg-ink-950">
        <img
          src={current}
          alt={name}
          className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.03]"
          loading="lazy"
        />
        {urls.length > 1 ? (
          <>
            <button
              type="button"
              className="product-gallery__nav absolute top-1/2 left-2 size-8 -translate-y-1/2"
              aria-label="Предыдущее фото"
              onClick={(event) => {
                stop(event);
                setIndex((i) => (i - 1 + urls.length) % urls.length);
              }}
            >
              <ChevronLeft className="size-4" />
            </button>
            <button
              type="button"
              className="product-gallery__nav absolute top-1/2 right-2 size-8 -translate-y-1/2"
              aria-label="Следующее фото"
              onClick={(event) => {
                stop(event);
                setIndex((i) => (i + 1) % urls.length);
              }}
            >
              <ChevronRight className="size-4" />
            </button>
            <div className="absolute bottom-2 left-1/2 flex -translate-x-1/2 gap-1.5">
              {urls.map((_, i) => (
                <button
                  key={i}
                  type="button"
                  aria-label={`Фото ${i + 1}`}
                  className={`size-1.5 rounded-full ${
                    i === index ? "bg-white" : "bg-white/40"
                  }`}
                  onClick={(event) => {
                    stop(event);
                    setIndex(i);
                  }}
                />
              ))}
            </div>
          </>
        ) : null}
      </div>
    );
  }

  return (
    <Link
      to={openHref}
      className="group block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-glow-violet/40"
      aria-label={`Открыть ${name}`}
    >
      {media}
    </Link>
  );
}

function ProductsViewToggle({
  value,
  onChange,
}: {
  value: ProductsView;
  onChange: (view: ProductsView) => void;
}) {
  return (
    <div
      className="boxes-view-toggle"
      role="group"
      aria-label="Вид каталога"
    >
      <button
        type="button"
        className={`boxes-view-toggle__btn ${value === "grid" ? "is-active" : ""}`}
        aria-pressed={value === "grid"}
        aria-label="Сетка"
        title="Сетка"
        onClick={() => onChange("grid")}
      >
        <LayoutGrid className="size-4" strokeWidth={2.25} />
      </button>
      <button
        type="button"
        className={`boxes-view-toggle__btn ${value === "list" ? "is-active" : ""}`}
        aria-pressed={value === "list"}
        aria-label="Список"
        title="Список"
        onClick={() => onChange("list")}
      >
        <List className="size-4" strokeWidth={2.25} />
      </button>
    </div>
  );
}

export function ProductsPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const [view, setView] = useState<ProductsView>(() =>
    resolveInitialProductsView(),
  );

  const productsQuery = useQuery({
    queryKey: ["products"],
    queryFn: api.products,
  });

  const addItem = useMutation({
    mutationFn: (payload: { sku: string; quantity: number }) =>
      api.addCartItem(payload),
    onSuccess: (cart) => {
      queryClient.setQueryData<Cart>(["cart"], cart);
    },
  });

  const setProductsView = (next: ProductsView) => {
    setView(next);
    window.localStorage.setItem(PRODUCTS_VIEW_STORAGE_KEY, next);
  };

  const addToCart = (product: Product) => {
    if (!isAuthenticated) {
      navigate("/login", { state: { from: "/products" } });
      return;
    }
    addItem.mutate({ sku: product.sku, quantity: 1 });
  };

  const products = productsQuery.data ?? [];
  const showProducts = productsQuery.isSuccess && products.length > 0;

  if (productsQuery.isPending) {
    return <Spinner label="Загружаем товары…" className="py-32" />;
  }

  if (productsQuery.isError) {
    return (
      <PageTransition>
        <div className="glass-soft mt-16 p-8 text-center text-sm text-rose-200">
          Не удалось загрузить товары
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="pt-10 pb-10 sm:pt-14">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <p className="chip w-fit">
              <Package className="size-3.5" />
              Товары
            </p>
            <h1 className="mt-3 font-sans text-2xl font-semibold tracking-tight sm:text-3xl">
              Каталог
            </h1>
            <p className="mt-2 max-w-xl text-sm text-slate-400">
              Выберите товар и добавьте в корзину. После оплаты кредиты появятся
              на балансе.
            </p>
          </motion.div>
          {showProducts ? (
            <ProductsViewToggle value={view} onChange={setProductsView} />
          ) : null}
        </div>

        <section className="mt-8">
          {!products.length ? (
            <p className="glass p-6 text-sm text-slate-400">
              Пока нет активных товаров.
            </p>
          ) : null}

          {showProducts && view === "grid" ? (
            <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {products.map((product: Product, index) => (
                <motion.li
                  key={product.id}
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.04 }}
                  className="glass flex flex-col overflow-hidden !rounded-2xl"
                >
                  <ProductGallery
                    urls={product.image_urls ?? []}
                    name={product.name}
                    fallback={
                      product.sku === "box_credit" ? "gift" : "package"
                    }
                    openHref={`/products/${product.id}`}
                  />
                  <div className="flex flex-1 flex-col p-5">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h2 className="font-sans text-lg font-semibold">
                          <Link
                            to={`/products/${product.id}`}
                            className="products-card__title text-slate-100 transition hover:opacity-80"
                          >
                            {product.name}
                          </Link>
                        </h2>
                      </div>
                      <ProductPrice
                        className="shrink-0 text-base"
                        unitPrice={product.unit_price}
                        currency={product.currency}
                        saleUnitPrice={product.sale_unit_price}
                        saleDiscountPercent={product.sale_discount_percent}
                      />
                    </div>
                    {product.description ? (
                      <p className="products-card__desc mt-3 flex-1 text-sm leading-relaxed text-slate-400">
                        {product.description}
                      </p>
                    ) : (
                      <div className="flex-1" />
                    )}
                    <button
                      type="button"
                      className="btn-primary mt-5 w-full justify-center"
                      disabled={addItem.isPending}
                      onClick={() => addToCart(product)}
                    >
                      <Plus className="size-3.5" />
                      В корзину
                    </button>
                    {addItem.isError ? (
                      <p className="mt-2 text-xs text-rose-300" role="alert">
                        {(addItem.error as ApiError)?.message ??
                          "Не удалось добавить"}
                      </p>
                    ) : null}
                  </div>
                </motion.li>
              ))}
            </ul>
          ) : null}

          {showProducts && view === "list" ? (
            <div className="boxes-list flex flex-col gap-2.5">
              {products.map((product: Product, index) => (
                <motion.article
                  key={product.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: Math.min(index, 10) * 0.03 }}
                  className="boxes-list__row glass relative flex gap-3 !rounded-xl p-2.5 sm:gap-4 sm:p-3"
                >
                  <Link
                    to={`/products/${product.id}`}
                    className="boxes-list__cover transition hover:opacity-90"
                    aria-label={`Открыть ${product.name}`}
                  >
                    <ProductThumb
                      urls={product.image_urls ?? []}
                      name={product.name}
                      fallback={
                        product.sku === "box_credit" ? "gift" : "package"
                      }
                      className="h-full min-h-[4.75rem] w-full"
                    />
                  </Link>

                  <div className="min-w-0 flex-1">
                    <h2 className="truncate font-sans text-sm font-semibold sm:text-base">
                      <Link
                        to={`/products/${product.id}`}
                        className="products-card__title transition hover:opacity-80"
                      >
                        {product.name}
                      </Link>
                    </h2>
                    {product.description ? (
                      <p className="products-card__desc mt-1 line-clamp-1 text-xs text-slate-400 sm:text-sm">
                        {product.description}
                      </p>
                    ) : null}
                  </div>

                  <div className="boxes-list__actions flex shrink-0 flex-col items-end gap-1.5">
                    <ProductPrice
                      className="text-sm"
                      align="end"
                      unitPrice={product.unit_price}
                      currency={product.currency}
                      saleUnitPrice={product.sale_unit_price}
                      saleDiscountPercent={product.sale_discount_percent}
                    />
                    <button
                      type="button"
                      className="btn-primary px-3 py-1.5 text-xs"
                      disabled={addItem.isPending}
                      onClick={() => addToCart(product)}
                    >
                      <Plus className="size-3.5" />
                      <span className="hidden sm:inline">В корзину</span>
                    </button>
                  </div>
                </motion.article>
              ))}
            </div>
          ) : null}

          {showProducts && addItem.isError ? (
            <p className="mt-3 text-xs text-rose-300" role="alert">
              {(addItem.error as ApiError)?.message ?? "Не удалось добавить"}
            </p>
          ) : null}
        </section>
      </div>
    </PageTransition>
  );
}
