import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Copy,
  Percent,
  Plus,
  Ticket,
} from "lucide-react";

import { CardActionsMenu } from "../components/CardActionsMenu";
import { Modal } from "../components/Modal";
import { PageTransition } from "../components/PageTransition";
import { Spinner } from "../components/Spinner";
import { useToast } from "../components/Toast";
import { ApiError, api } from "../lib/api";
import { formatDateTime, pluralize } from "../lib/format";
import type { PromoCode } from "../lib/types";

const DISCOUNT_OPTIONS = Array.from({ length: 20 }, (_, i) => (i + 1) * 5);

const FIELD =
  "mt-1.5 w-full rounded-xl border border-white/10 bg-ink-900/60 px-3 py-2 text-sm text-slate-100 outline-none focus:border-glow-cyan/50";

function defaultExpiresLocal(): string {
  const d = new Date();
  d.setDate(d.getDate() + 30);
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
  return d.toISOString().slice(0, 16);
}

export function AdminPromoCodesPage() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [code, setCode] = useState("");
  const [discount, setDiscount] = useState(20);
  const [expiresAt, setExpiresAt] = useState(defaultExpiresLocal);

  const promoQuery = useQuery({
    queryKey: ["admin-promo-codes"],
    queryFn: api.adminPromoCodes,
  });

  const resetForm = () => {
    setCode("");
    setDiscount(20);
    setExpiresAt(defaultExpiresLocal());
  };

  const closeModal = () => {
    setModalOpen(false);
    resetForm();
  };

  const createMutation = useMutation({
    mutationFn: () =>
      api.createAdminPromoCode({
        code: code.trim().toUpperCase(),
        discount_percent: discount,
        expires_at: new Date(expiresAt).toISOString(),
      }),
    onSuccess: (promo) => {
      void queryClient.invalidateQueries({ queryKey: ["admin-promo-codes"] });
      closeModal();
      toast(`Промокод ${promo.code} создан`, "success");
    },
    onError: (error) => {
      toast((error as ApiError).message ?? "Не удалось создать", "error");
    },
  });

  const promos = promoQuery.data ?? [];
  const canSubmit = useMemo(() => {
    const normalized = code.trim().toUpperCase();
    return (
      normalized.length >= 4 &&
      normalized.length <= 20 &&
      /^[A-Z0-9]+$/.test(normalized) &&
      Boolean(expiresAt) &&
      !createMutation.isPending
    );
  }, [code, expiresAt, createMutation.isPending]);

  const copyCode = async (value: string) => {
    try {
      await navigator.clipboard.writeText(value);
      toast("Код скопирован", "success");
    } catch {
      toast("Не удалось скопировать", "error");
    }
  };

  if (promoQuery.isPending) {
    return <Spinner label="Загружаем промокоды…" className="py-32" />;
  }

  if (promoQuery.isError) {
    return (
      <PageTransition>
        <div className="glass-soft mt-16 p-8 text-center text-sm text-rose-200">
          {(promoQuery.error as Error).message}
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="pt-10 pb-10 sm:pt-14">
        <Link
          to="/app/panel"
          className="btn-ghost inline-flex items-center gap-2 px-3 py-2 text-sm"
        >
          <ArrowLeft className="size-4" />
          К панели
        </Link>

        <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="chip w-fit">
              <Ticket className="size-3.5" />
              Панель
            </p>
            <h1 className="mt-3 font-sans text-2xl font-semibold tracking-tight sm:text-3xl">
              Промокоды
            </h1>
          </div>
          <button
            type="button"
            className="btn-primary"
            onClick={() => {
              resetForm();
              setModalOpen(true);
            }}
          >
            <Plus className="size-4" />
            Новый промокод
          </button>
        </div>

        <section className="mt-8">
          {!promos.length ? (
            <p className="text-sm text-slate-400">Пока нет промокодов.</p>
          ) : (
            <div className="boxes-list flex flex-col gap-2.5">
              {promos.map((promo: PromoCode, index) => (
                <motion.article
                  key={promo.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: Math.min(index, 10) * 0.03 }}
                  className="boxes-list__row glass relative flex items-center gap-3 !rounded-xl p-2.5 sm:gap-4 sm:p-3"
                >
                  <div className="boxes-list__cover shrink-0 overflow-hidden rounded-lg">
                    <div className="grid h-[4.5rem] w-[4.5rem] place-items-center bg-gradient-to-br from-glow-violet/15 via-transparent to-glow-cyan/10 sm:h-16 sm:w-28">
                      <Ticket
                        className="size-7 text-glow-violet/80"
                        strokeWidth={1.5}
                      />
                    </div>
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="truncate font-mono text-sm font-semibold tracking-wider sm:text-base">
                        {promo.code}
                      </h2>
                      <span className="status-badge status-badge--active">
                        <Percent
                          className="status-badge__icon"
                          strokeWidth={2.25}
                        />
                        <span>{promo.discount_percent}%</span>
                      </span>
                    </div>
                    <p className="mt-1 truncate text-xs text-slate-400 sm:text-sm">
                      до {formatDateTime(promo.expires_at)}
                      {!promo.is_active ? " · неактивен" : ""}
                    </p>
                  </div>

                  <div className="hidden items-center gap-2 md:flex">
                    <span className="chip px-2 py-0.5">
                      <Ticket className="size-3.5" />
                      {promo.usage_count}{" "}
                      {pluralize(promo.usage_count, [
                        "использование",
                        "использования",
                        "использований",
                      ])}
                    </span>
                  </div>

                  <div className="flex shrink-0 items-center gap-1">
                    <button
                      type="button"
                      className="btn-ghost hidden px-3 py-1.5 text-xs sm:inline-flex"
                      onClick={() => void copyCode(promo.code)}
                    >
                      <Copy className="size-3.5" />
                      Код
                    </button>
                    <CardActionsMenu
                      label={`Действия с промокодом ${promo.code}`}
                      items={[
                        {
                          key: "copy",
                          label: "Скопировать код",
                          icon: <Copy className="size-3.5" />,
                          onClick: () => void copyCode(promo.code),
                        },
                      ]}
                    />
                  </div>
                </motion.article>
              ))}
            </div>
          )}
        </section>
      </div>

      <Modal
        open={modalOpen}
        title="Новый промокод"
        onClose={closeModal}
        footer={
          <>
            <button type="button" className="btn-ghost" onClick={closeModal}>
              Отмена
            </button>
            <button
              type="submit"
              form="admin-promo-create-form"
              className="btn-primary"
              disabled={!canSubmit}
            >
              Создать
            </button>
          </>
        }
      >
        <form
          id="admin-promo-create-form"
          className="grid gap-4"
          onSubmit={(e) => {
            e.preventDefault();
            if (canSubmit) createMutation.mutate();
          }}
        >
          <label className="block text-sm text-slate-400">
            Код
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              maxLength={20}
              placeholder="SUMMER25"
              className={`${FIELD} font-mono tracking-wider uppercase`}
              autoComplete="off"
              spellCheck={false}
              autoFocus
            />
          </label>
          <label className="block text-sm text-slate-400">
            Скидка
            <select
              value={discount}
              onChange={(e) => setDiscount(Number(e.target.value))}
              className={FIELD}
            >
              {DISCOUNT_OPTIONS.map((value) => (
                <option key={value} value={value}>
                  {value}%
                  {value === 100 ? " (бесплатно)" : ""}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm text-slate-400">
            Действует до
            <input
              type="datetime-local"
              value={expiresAt}
              onChange={(e) => setExpiresAt(e.target.value)}
              className={FIELD}
            />
          </label>
        </form>
      </Modal>
    </PageTransition>
  );
}
