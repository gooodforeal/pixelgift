import { useEffect, useId, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import {
  Gift,
  Minus,
  Package,
  Plus,
  ShoppingBag,
  Ticket,
  Trash2,
} from "lucide-react";

import { ApiError, api, toProxiedAssetUrl } from "../lib/api";
import type { Cart, CartItem } from "../lib/types";
import { Spinner } from "./Spinner";

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

function CartItemThumb({ item }: { item: CartItem }) {
  const urls = item.image_urls ?? [];
  const fallbackGift =
    item.sku.includes("box") || item.name.toLowerCase().includes("бокс");

  if (!urls.length) {
    const Icon = fallbackGift ? Gift : Package;
    return (
      <div className="cart-dropdown__thumb cart-dropdown__thumb--empty">
        <Icon
          className={`size-5 ${
            fallbackGift ? "text-glow-cyan/80" : "text-glow-violet/70"
          }`}
          strokeWidth={1.5}
        />
      </div>
    );
  }

  return (
    <img
      src={toProxiedAssetUrl(urls[0]!)}
      alt=""
      className="cart-dropdown__thumb"
      loading="lazy"
    />
  );
}

interface CartDropdownProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  cartCount: number;
}

export function CartDropdown({
  open,
  onOpenChange,
  cartCount,
}: CartDropdownProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const rootRef = useRef<HTMLDivElement>(null);
  const panelId = useId();
  const [promoCode, setPromoCode] = useState("");

  const cartQuery = useQuery({
    queryKey: ["cart"],
    queryFn: api.cart,
    enabled: open,
  });

  useEffect(() => {
    if (!open) return;

    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node | null;
      if (!target || rootRef.current?.contains(target)) return;
      onOpenChange(false);
    };

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onOpenChange(false);
    };

    window.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("pointerdown", onPointerDown);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [open, onOpenChange]);

  const invalidate = async () => {
    await queryClient.invalidateQueries({ queryKey: ["cart"] });
    await queryClient.invalidateQueries({ queryKey: ["balances"] });
    await queryClient.invalidateQueries({ queryKey: ["balance-logs"] });
  };

  const updateItem = useMutation({
    mutationFn: (payload: { productId: string; quantity: number }) =>
      api.updateCartItem(payload.productId, payload.quantity),
    onSuccess: (cart) => {
      queryClient.setQueryData<Cart>(["cart"], cart);
    },
  });

  const removeItem = useMutation({
    mutationFn: (productId: string) => api.removeCartItem(productId),
    onSuccess: (cart) => {
      queryClient.setQueryData<Cart>(["cart"], cart);
    },
  });

  const checkout = useMutation({
    mutationFn: () =>
      api.checkoutCart({
        promo_code: promoCode.trim() ? promoCode.trim().toUpperCase() : null,
      }),
    onSuccess: async (result) => {
      await invalidate();
      setPromoCode("");
      onOpenChange(false);
      if (result.confirmation_url) {
        window.location.href = result.confirmation_url;
        return;
      }
      navigate("/app/profile");
    },
  });

  const cart = cartQuery.data ?? queryClient.getQueryData<Cart>(["cart"]);
  const busy =
    updateItem.isPending || removeItem.isPending || checkout.isPending;

  const trigger = (
    <button
      type="button"
      className={`app-rail__link ${open ? "is-active" : ""}`}
      aria-label={cartCount > 0 ? `Корзина, ${cartCount}` : "Корзина"}
      title="Корзина"
      aria-expanded={open}
      aria-controls={panelId}
      aria-haspopup="dialog"
      onClick={() => onOpenChange(!open)}
    >
      <span className="app-rail__hit">
        <span className="app-rail__icon">
          <span className="relative inline-flex">
            <ShoppingBag className="size-5" strokeWidth={2} />
            {cartCount > 0 ? (
              <span className="app-rail__badge" aria-hidden>
                {cartCount > 99 ? "99+" : cartCount}
              </span>
            ) : null}
          </span>
        </span>
      </span>
    </button>
  );

  return (
    <div ref={rootRef} className="relative">
      {trigger}

      <AnimatePresence>
        {open ? (
          <motion.div
            id={panelId}
            role="dialog"
            aria-label="Корзина"
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
            className="cart-dropdown absolute top-full right-0 z-[60] mt-2"
          >
            <div className="cart-dropdown__glow" aria-hidden />

            <div className="cart-dropdown__head">
              <div className="flex min-w-0 items-center gap-2.5">
                <span className="cart-dropdown__head-icon">
                  <ShoppingBag className="size-4" strokeWidth={2} />
                </span>
                <div className="min-w-0">
                  <p className="cart-dropdown__title">Корзина</p>
                  <p className="cart-dropdown__subtitle">
                    {cartCount > 0
                      ? `${cartCount} ${
                          cartCount === 1
                            ? "товар"
                            : cartCount < 5
                              ? "товара"
                              : "товаров"
                        }`
                      : "пока пусто"}
                  </p>
                </div>
              </div>
              {cartCount > 0 ? (
                <span className="chip px-2.5 py-1 tabular-nums">
                  {cartCount} шт.
                </span>
              ) : null}
            </div>

            <div className="cart-dropdown__body">
              {cartQuery.isPending && !cart ? (
                <Spinner label="Загружаем…" className="py-8" />
              ) : cartQuery.isError && !cart ? (
                <p className="px-1 py-6 text-center text-sm text-rose-300">
                  Не удалось загрузить корзину
                </p>
              ) : !cart?.items.length ? (
                <div className="cart-dropdown__empty-state">
                  <span className="cart-dropdown__empty-icon">
                    <ShoppingBag className="size-6" strokeWidth={1.5} />
                  </span>
                  <p className="cart-dropdown__empty">Корзина пуста</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Добавьте кредиты или товары из каталога
                  </p>
                  <Link
                    to="/products"
                    className="btn-primary mt-4 px-4 py-2 text-xs"
                    onClick={() => onOpenChange(false)}
                  >
                    В каталог
                  </Link>
                </div>
              ) : (
                <>
                  <ul className="cart-dropdown__list">
                    {cart.items.map((item, index) => (
                      <motion.li
                        key={item.product_id}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: Math.min(index, 6) * 0.04 }}
                        className="cart-dropdown__item"
                      >
                        <CartItemThumb item={item} />

                        <div className="min-w-0 flex-1">
                          <div className="flex items-start justify-between gap-2">
                            <p className="cart-dropdown__item-name">
                              {item.name}
                            </p>
                            <button
                              type="button"
                              className="cart-dropdown__remove"
                              disabled={busy}
                              aria-label={`Удалить ${item.name}`}
                              onClick={() =>
                                removeItem.mutate(item.product_id)
                              }
                            >
                              <Trash2 className="size-3.5" />
                            </button>
                          </div>

                          {item.compare_at_price != null &&
                          item.sale_discount_percent != null ? (
                            <div className="mt-1 flex flex-wrap items-center gap-1.5">
                              <span className="sale-badge">
                                −{item.sale_discount_percent}%
                              </span>
                              <span className="text-[11px] text-slate-500 line-through">
                                {formatPrice(
                                  item.compare_at_price,
                                  item.currency,
                                )}
                              </span>
                              <span className="text-[11px] font-medium text-emerald-300">
                                {formatPrice(item.unit_price, item.currency)}
                              </span>
                            </div>
                          ) : (
                            <p className="mt-1 text-[11px] text-slate-500">
                              {formatPrice(item.unit_price, item.currency)} / шт.
                            </p>
                          )}

                          <div className="mt-2.5 flex items-center justify-between gap-2">
                            <div className="cart-dropdown__qty">
                              <button
                                type="button"
                                className="cart-dropdown__qty-btn"
                                disabled={busy || item.quantity <= 1}
                                aria-label="Уменьшить"
                                onClick={() =>
                                  updateItem.mutate({
                                    productId: item.product_id,
                                    quantity: item.quantity - 1,
                                  })
                                }
                              >
                                <Minus className="size-3.5" />
                              </button>
                              <span className="cart-dropdown__qty-value">
                                {item.quantity}
                              </span>
                              <button
                                type="button"
                                className="cart-dropdown__qty-btn"
                                disabled={busy}
                                aria-label="Увеличить"
                                onClick={() =>
                                  updateItem.mutate({
                                    productId: item.product_id,
                                    quantity: item.quantity + 1,
                                  })
                                }
                              >
                                <Plus className="size-3.5" />
                              </button>
                            </div>
                            <p className="cart-dropdown__line-total">
                              {formatPrice(item.amount, item.currency)}
                            </p>
                          </div>
                        </div>
                      </motion.li>
                    ))}
                  </ul>

                  <div className="cart-dropdown__footer">
                    <label className="cart-dropdown__promo-label">
                      <span className="inline-flex items-center gap-1.5">
                        <Ticket className="size-3.5 text-glow-violet/80" />
                        Промокод
                      </span>
                      <input
                        type="text"
                        value={promoCode}
                        onChange={(e) =>
                          setPromoCode(e.target.value.toUpperCase())
                        }
                        maxLength={20}
                        placeholder="введите промокод"
                        className="cart-dropdown__promo"
                        disabled={busy}
                        autoComplete="off"
                        spellCheck={false}
                      />
                    </label>

                    <div className="cart-dropdown__checkout">
                      <div className="min-w-0">
                        <p className="cart-dropdown__total-label">Итого</p>
                        <p className="cart-dropdown__total-value">
                          {formatPrice(cart.total_amount, cart.currency)}
                        </p>
                      </div>
                      <button
                        type="button"
                        className="btn-primary cart-dropdown__pay"
                        disabled={busy}
                        onClick={() => checkout.mutate()}
                      >
                        {checkout.isPending ? "Оплата…" : "Оплатить"}
                      </button>
                    </div>

                    {checkout.isError ? (
                      <p className="text-xs text-rose-300" role="alert">
                        {(checkout.error as ApiError)?.message ??
                          "Не удалось создать платёж"}
                      </p>
                    ) : null}
                  </div>
                </>
              )}
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
