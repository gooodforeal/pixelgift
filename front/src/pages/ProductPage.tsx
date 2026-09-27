import { useMemo, useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Gift,
  Minus,
  Package,
  Plus,
  ShoppingBag,
} from "lucide-react";

import { PageTransition } from "../components/PageTransition";
import { ProductPrice } from "../components/ProductPrice";
import { Spinner } from "../components/Spinner";
import { useToast } from "../components/Toast";
import { useAuth } from "../hooks/useAuth";
import { ApiError, api, toProxiedAssetUrl } from "../lib/api";
import type { Cart, Product } from "../lib/types";

function ProductGallery({
  urls,
  name,
  fallback,
}: {
  urls: string[];
  name: string;
  fallback: "gift" | "package";
}) {
  const [index, setIndex] = useState(0);
  if (!urls.length) {
    const Icon = fallback === "gift" ? Gift : Package;
    return (
      <div className="flex aspect-[4/3] items-center justify-center bg-gradient-to-br from-glow-cyan/15 via-ink-950/40 to-glow-violet/15 sm:aspect-square">
        <Icon
          className={`size-16 ${
            fallback === "gift" ? "text-glow-cyan/80" : "text-slate-500/70"
          }`}
          strokeWidth={1.5}
        />
      </div>
    );
  }
  const current = toProxiedAssetUrl(urls[index] ?? urls[0]!);
  return (
    <div className="relative aspect-[4/3] overflow-hidden bg-ink-950 sm:aspect-square">
      <img
        src={current}
        alt={name}
        className="h-full w-full object-cover"
        loading="lazy"
      />
      {urls.length > 1 ? (
        <>
          <button
            type="button"
            className="product-gallery__nav absolute top-1/2 left-3 size-9 -translate-y-1/2"
            aria-label="Предыдущее фото"
            onClick={() =>
              setIndex((i) => (i - 1 + urls.length) % urls.length)
            }
          >
            <ChevronLeft className="size-4" />
          </button>
          <button
            type="button"
            className="product-gallery__nav absolute top-1/2 right-3 size-9 -translate-y-1/2"
            aria-label="Следующее фото"
            onClick={() => setIndex((i) => (i + 1) % urls.length)}
          >
            <ChevronRight className="size-4" />
          </button>
          <div className="absolute bottom-3 left-1/2 flex -translate-x-1/2 gap-1.5">
            {urls.map((_, i) => (
              <button
                key={i}
                type="button"
                aria-label={`Фото ${i + 1}`}
                className={`size-2 rounded-full transition ${
                  i === index ? "bg-white" : "bg-white/40 hover:bg-white/60"
                }`}
                onClick={() => setIndex(i)}
              />
            ))}
          </div>
        </>
      ) : null}
    </div>
  );
}

export function ProductPage() {
  const { productId = "" } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const toast = useToast();
  const [quantity, setQuantity] = useState(1);

  const productsQuery = useQuery({
    queryKey: ["products"],
    queryFn: api.products,
  });

  const product = useMemo(
    () => productsQuery.data?.find((item) => item.id === productId) ?? null,
    [productsQuery.data, productId],
  );

  const addItem = useMutation({
    mutationFn: (payload: { sku: string; quantity: number }) =>
      api.addCartItem(payload),
    onSuccess: (cart) => {
      queryClient.setQueryData<Cart>(["cart"], cart);
      toast("Добавлено в корзину", "success");
    },
    onError: (error) => {
      toast(
        (error as ApiError)?.message ?? "Не удалось добавить в корзину",
        "error",
      );
    },
  });

  const onSubmit = (event: FormEvent, item: Product) => {
    event.preventDefault();
    if (!isAuthenticated) {
      navigate("/login", { state: { from: `/products/${item.id}` } });
      return;
    }
    addItem.mutate({ sku: item.sku, quantity });
  };

  if (productsQuery.isPending) {
    return <Spinner label="Загружаем товар…" className="py-32" />;
  }

  if (productsQuery.isError) {
    return (
      <PageTransition>
        <div className="glass-soft mt-16 p-8 text-center text-sm text-rose-200">
          Не удалось загрузить товар
        </div>
      </PageTransition>
    );
  }

  if (!product) {
    return (
      <PageTransition>
        <div className="pt-10 pb-10 text-center sm:pt-14">
          <p className="text-sm text-slate-400">Товар не найден или снят с продажи.</p>
          <Link to="/products" className="btn-ghost mt-4 inline-flex">
            <ArrowLeft className="size-4" />
            К каталогу
          </Link>
        </div>
      </PageTransition>
    );
  }

  const fallback = product.sku === "box_credit" ? "gift" : "package";

  return (
    <PageTransition>
      <div className="pt-10 pb-12 sm:pt-14">
        <Link
          to="/products"
          className="btn-ghost inline-flex items-center gap-2 px-3 py-2 text-sm"
        >
          <ArrowLeft className="size-4" />
          К каталогу
        </Link>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-5 grid gap-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)] lg:gap-8"
        >
          <div className="glass overflow-hidden !rounded-2xl">
            <ProductGallery
              urls={product.image_urls ?? []}
              name={product.name}
              fallback={fallback}
            />
          </div>

          <div className="flex flex-col">
            <p className="chip w-fit">
              <Package className="size-3.5" />
              Товар
            </p>
            <h1 className="mt-3 font-sans text-2xl font-semibold tracking-tight sm:text-3xl">
              {product.name}
            </h1>

            <div className="mt-4">
              <ProductPrice
                className="text-xl"
                unitPrice={product.unit_price}
                currency={product.currency}
                saleUnitPrice={product.sale_unit_price}
                saleDiscountPercent={product.sale_discount_percent}
              />
            </div>

            {product.description ? (
              <p className="product-page__desc mt-5 text-sm leading-relaxed text-slate-400 sm:text-base">
                {product.description}
              </p>
            ) : null}

            <form
              className="product-buy-form glass mt-8 flex flex-col gap-6 !rounded-2xl p-4 sm:gap-7 sm:p-5"
              onSubmit={(event) => onSubmit(event, product)}
            >
              <div className="flex flex-wrap items-center gap-3">
                <span className="product-buy-form__label text-xs font-medium text-slate-400">
                  Количество
                </span>
                <div className="product-qty">
                  <button
                    type="button"
                    className="product-qty__btn"
                    disabled={quantity <= 1 || addItem.isPending}
                    aria-label="Уменьшить"
                    onClick={() => setQuantity((value) => Math.max(1, value - 1))}
                  >
                    <Minus className="size-3.5" />
                  </button>
                  <span className="product-qty__value">{quantity}</span>
                  <button
                    type="button"
                    className="product-qty__btn"
                    disabled={quantity >= 99 || addItem.isPending}
                    aria-label="Увеличить"
                    onClick={() =>
                      setQuantity((value) => Math.min(99, value + 1))
                    }
                  >
                    <Plus className="size-3.5" />
                  </button>
                </div>
              </div>

              <button
                type="submit"
                className="btn-primary w-full justify-center"
                disabled={addItem.isPending}
              >
                <ShoppingBag className="size-4" />
                {addItem.isPending ? "Добавляем…" : "В корзину"}
              </button>
            </form>
          </div>
        </motion.div>
      </div>
    </PageTransition>
  );
}
