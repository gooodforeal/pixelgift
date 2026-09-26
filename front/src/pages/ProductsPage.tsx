import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ChevronLeft,
  ChevronRight,
  Gift,
  Package,
  Plus,
} from "lucide-react";

import { PageTransition } from "../components/PageTransition";
import { Spinner } from "../components/Spinner";
import { useAuth } from "../hooks/useAuth";
import { ApiError, api, toProxiedAssetUrl } from "../lib/api";
import type { Cart, Product } from "../lib/types";

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
      <div className="flex h-44 items-center justify-center bg-gradient-to-br from-glow-cyan/10 via-transparent to-glow-violet/10">
        <Icon
          className={`size-12 ${
            fallback === "gift" ? "text-glow-cyan/80" : "text-slate-500/70"
          }`}
          strokeWidth={1.5}
        />
      </div>
    );
  }
  const current = toProxiedAssetUrl(urls[index] ?? urls[0]!);
  return (
    <div className="relative h-44 overflow-hidden bg-ink-950/40">
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
            className="btn-ghost absolute top-1/2 left-2 size-8 -translate-y-1/2 bg-ink-950/50 px-0!"
            aria-label="Предыдущее фото"
            onClick={() =>
              setIndex((i) => (i - 1 + urls.length) % urls.length)
            }
          >
            <ChevronLeft className="size-4" />
          </button>
          <button
            type="button"
            className="btn-ghost absolute top-1/2 right-2 size-8 -translate-y-1/2 bg-ink-950/50 px-0!"
            aria-label="Следующее фото"
            onClick={() => setIndex((i) => (i + 1) % urls.length)}
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
                onClick={() => setIndex(i)}
              />
            ))}
          </div>
        </>
      ) : null}
    </div>
  );
}

export function ProductsPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

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

  const products = productsQuery.data ?? [];

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

        <section className="mt-8">
          {!products.length ? (
            <p className="glass p-6 text-sm text-slate-400">
              Пока нет активных товаров.
            </p>
          ) : (
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
                  />
                  <div className="flex flex-1 flex-col p-5">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h2 className="font-sans text-lg font-semibold text-slate-100">
                          {product.name}
                        </h2>
                      </div>
                      <p className="shrink-0 text-base font-semibold text-white">
                        {formatPrice(product.unit_price, product.currency)}
                      </p>
                    </div>
                    {product.description ? (
                      <p className="mt-3 flex-1 text-sm leading-relaxed text-slate-400">
                        {product.description}
                      </p>
                    ) : (
                      <div className="flex-1" />
                    )}
                    <button
                      type="button"
                      className="btn-primary mt-5 w-full justify-center"
                      disabled={addItem.isPending}
                      onClick={() => {
                        if (!isAuthenticated) {
                          navigate("/login", {
                            state: { from: "/products" },
                          });
                          return;
                        }
                        addItem.mutate({ sku: product.sku, quantity: 1 });
                      }}
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
          )}
        </section>
      </div>
    </PageTransition>
  );
}
