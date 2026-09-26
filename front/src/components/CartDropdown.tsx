import { useEffect, useId, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { Minus, Plus, ShoppingCart, Trash2 } from "lucide-react";

import { ApiError, api } from "../lib/api";
import type { Cart } from "../lib/types";
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
            <ShoppingCart className="size-5" strokeWidth={2} />
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
            transition={{ duration: 0.16 }}
            className="cart-dropdown absolute top-full right-0 z-[60] mt-2"
          >
            <div className="cart-dropdown__head">
              <p className="font-sans text-sm font-semibold text-slate-100">
                Корзина
              </p>
              {cartCount > 0 ? (
                <span className="text-xs text-slate-500 tabular-nums">
                  {cartCount} шт.
                </span>
              ) : null}
            </div>

            <div className="cart-dropdown__body">
              {cartQuery.isPending && !cart ? (
                <Spinner label="Загружаем…" className="py-6" />
              ) : cartQuery.isError && !cart ? (
                <p className="px-1 py-4 text-center text-sm text-rose-300">
                  Не удалось загрузить корзину
                </p>
              ) : !cart?.items.length ? (
                <div className="px-1 py-5 text-center">
                  <p className="text-sm text-slate-400">Корзина пуста</p>
                  <Link
                    to="/products"
                    className="btn-ghost mt-3 inline-flex text-xs"
                    onClick={() => onOpenChange(false)}
                  >
                    В каталог
                  </Link>
                </div>
              ) : (
                <>
                  <ul className="space-y-2">
                    {cart.items.map((item) => (
                      <li
                        key={item.product_id}
                        className="rounded-xl border border-white/10 bg-ink-900/40 px-3 py-2.5"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium text-slate-100">
                              {item.name}
                            </p>
                            <p className="mt-0.5 text-[11px] text-slate-500">
                              {formatPrice(item.unit_price, item.currency)}
                            </p>
                          </div>
                          <button
                            type="button"
                            className="btn-ghost size-7 shrink-0 px-0! text-rose-300"
                            disabled={busy}
                            aria-label={`Удалить ${item.name}`}
                            onClick={() => removeItem.mutate(item.product_id)}
                          >
                            <Trash2 className="size-3.5" />
                          </button>
                        </div>
                        <div className="mt-2 flex items-center gap-1.5">
                          <button
                            type="button"
                            className="btn-ghost size-7 px-0!"
                            disabled={busy || item.quantity <= 1}
                            onClick={() =>
                              updateItem.mutate({
                                productId: item.product_id,
                                quantity: item.quantity - 1,
                              })
                            }
                          >
                            <Minus className="size-3.5" />
                          </button>
                          <span className="w-5 text-center text-sm tabular-nums">
                            {item.quantity}
                          </span>
                          <button
                            type="button"
                            className="btn-ghost size-7 px-0!"
                            disabled={busy}
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
                      </li>
                    ))}
                  </ul>

                  <div className="mt-3 space-y-3 border-t border-white/10 pt-3">
                    <label className="block text-xs text-slate-400">
                      Промокод
                      <input
                        type="text"
                        value={promoCode}
                        onChange={(e) =>
                          setPromoCode(e.target.value.toUpperCase())
                        }
                        maxLength={20}
                        placeholder="введите промокод"
                        className="mt-1.5 w-full rounded-xl border border-white/10 bg-ink-900/60 px-3 py-2 font-mono text-sm tracking-wider text-slate-100 outline-none placeholder:normal-case placeholder:tracking-normal focus:border-glow-cyan/50"
                        disabled={busy}
                        autoComplete="off"
                        spellCheck={false}
                      />
                    </label>
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm text-slate-300">
                        Итого:{" "}
                        <span className="font-semibold text-white">
                          {formatPrice(cart.total_amount, cart.currency)}
                        </span>
                      </p>
                      <button
                        type="button"
                        className="btn-primary px-3 py-2 text-xs"
                        disabled={busy}
                        onClick={() => checkout.mutate()}
                      >
                        Оплатить
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
