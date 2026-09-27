import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Copy,
  Percent,
  Plus,
  Power,
  PowerOff,
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
const PROMO_PAGE_SIZE = 10;

const FIELD = "field mt-1.5 !rounded-xl px-3 py-2";

const PROMO_STATUS_LABEL: Record<PromoCode["status"], string> = {
  active: "Активен",
  inactive: "Неактивен",
  expired: "Истёк",
  exhausted: "Исчерпан",
};

const PROMO_STATUS_BADGE: Record<PromoCode["status"], string> = {
  active: "status-badge--active",
  inactive: "status-badge--archived",
  expired: "status-badge--canceled",
  exhausted: "status-badge--pending",
};

function defaultExpiresLocal(): string {
  const d = new Date();
  d.setDate(d.getDate() + 30);
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
  return d.toISOString().slice(0, 16);
}

function PromoPagination({
  page,
  pageCount,
  total,
  pageSize,
  onChange,
}: {
  page: number;
  pageCount: number;
  total: number;
  pageSize: number;
  onChange: (page: number) => void;
}) {
  if (pageCount <= 1) return null;

  const from = (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);

  return (
    <nav
      className="boxes-pagination mt-6 flex flex-wrap items-center justify-between gap-3"
      aria-label="Страницы промокодов"
    >
      <p className="boxes-pagination__meta text-sm text-slate-400">
        {from}–{to} из {total}
      </p>
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="btn-ghost size-9 px-0 py-0 disabled:opacity-35"
          aria-label="Предыдущая страница"
          disabled={page <= 1}
          onClick={() => onChange(page - 1)}
        >
          <ChevronLeft className="size-4" />
        </button>
        <span className="boxes-pagination__page min-w-[4.5rem] text-center text-sm tabular-nums text-slate-300">
          {page} / {pageCount}
        </span>
        <button
          type="button"
          className="btn-ghost size-9 px-0 py-0 disabled:opacity-35"
          aria-label="Следующая страница"
          disabled={page >= pageCount}
          onClick={() => onChange(page + 1)}
        >
          <ChevronRight className="size-4" />
        </button>
      </div>
    </nav>
  );
}

function usageLabel(promo: PromoCode): string {
  if (promo.max_usages == null) {
    return `${promo.usage_count} ${pluralize(promo.usage_count, [
      "использование",
      "использования",
      "использований",
    ])}`;
  }
  return `${promo.usage_count} / ${promo.max_usages}`;
}

export function AdminPromoCodesPage() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [code, setCode] = useState("");
  const [discount, setDiscount] = useState(20);
  const [expiresAt, setExpiresAt] = useState(defaultExpiresLocal);
  const [maxUsages, setMaxUsages] = useState("");

  const promoQuery = useQuery({
    queryKey: ["admin-promo-codes", page, PROMO_PAGE_SIZE],
    queryFn: () => api.adminPromoCodes({ page, pageSize: PROMO_PAGE_SIZE }),
  });

  const resetForm = () => {
    setCode("");
    setDiscount(20);
    setExpiresAt(defaultExpiresLocal());
    setMaxUsages("");
  };

  const closeModal = () => {
    setModalOpen(false);
    resetForm();
  };

  const createMutation = useMutation({
    mutationFn: () => {
      const trimmedLimit = maxUsages.trim();
      const parsedLimit =
        trimmedLimit === "" ? null : Number.parseInt(trimmedLimit, 10);
      return api.createAdminPromoCode({
        code: code.trim().toUpperCase(),
        discount_percent: discount,
        expires_at: new Date(expiresAt).toISOString(),
        max_usages: parsedLimit,
      });
    },
    onSuccess: (promo) => {
      void queryClient.invalidateQueries({ queryKey: ["admin-promo-codes"] });
      setPage(1);
      closeModal();
      toast(`Промокод ${promo.code} создан`, "success");
    },
    onError: (error) => {
      toast((error as ApiError).message ?? "Не удалось создать", "error");
    },
  });

  const activeMutation = useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      api.setAdminPromoCodeActive(id, isActive),
    onSuccess: (promo) => {
      void queryClient.invalidateQueries({ queryKey: ["admin-promo-codes"] });
      toast(
        promo.is_active
          ? `Промокод ${promo.code} активирован`
          : `Промокод ${promo.code} деактивирован`,
        "success",
      );
    },
    onError: (error) => {
      toast((error as ApiError).message ?? "Не удалось обновить", "error");
    },
  });

  const total = promoQuery.data?.total ?? 0;
  const promos = promoQuery.data?.items ?? [];
  const pageCount = Math.max(1, Math.ceil(total / PROMO_PAGE_SIZE));
  const showPromos = promoQuery.isSuccess && total > 0;

  useEffect(() => {
    if (page > pageCount) setPage(pageCount);
  }, [page, pageCount]);

  const goToPage = (next: number) => {
    setPage(Math.min(pageCount, Math.max(1, next)));
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const canSubmit = useMemo(() => {
    const normalized = code.trim().toUpperCase();
    const trimmedLimit = maxUsages.trim();
    const limitOk =
      trimmedLimit === "" ||
      (/^\d+$/.test(trimmedLimit) && Number.parseInt(trimmedLimit, 10) >= 1);
    return (
      normalized.length >= 4 &&
      normalized.length <= 20 &&
      /^[A-Z0-9]+$/.test(normalized) &&
      Boolean(expiresAt) &&
      limitOk &&
      !createMutation.isPending
    );
  }, [code, expiresAt, maxUsages, createMutation.isPending]);

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
              Промокоды
            </p>
            <h1 className="mt-3 font-sans text-2xl font-semibold tracking-tight sm:text-3xl">
              Промокоды
            </h1>
            <p className="mt-2 text-sm text-slate-400">
              {total > 0
                ? `${total} ${pluralize(total, ["промокод", "промокода", "промокодов"])}`
                : "Здесь появятся промокоды"}
            </p>
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
          {!showPromos ? (
            <p className="text-sm text-slate-400">Пока нет промокодов.</p>
          ) : (
            <div className="boxes-list flex flex-col gap-2.5">
              {promos.map((promo: PromoCode, index) => (
                <motion.article
                  key={promo.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: Math.min(index, 10) * 0.03 }}
                  className="boxes-list__row glass relative flex gap-3 !rounded-xl p-2.5 sm:gap-4 sm:p-3"
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
                      <span
                        className={`status-badge ${PROMO_STATUS_BADGE[promo.status]}`}
                      >
                        {PROMO_STATUS_LABEL[promo.status]}
                      </span>
                      <span className="status-badge status-badge--active">
                        <Percent
                          className="status-badge__icon"
                          strokeWidth={2.25}
                        />
                        <span>{promo.discount_percent}%</span>
                      </span>
                      <span className="chip px-2 py-0.5">
                        <Ticket className="size-3.5" />
                        {usageLabel(promo)}
                      </span>
                    </div>
                    <p className="mt-1 truncate text-xs text-slate-400 sm:text-sm">
                      до {formatDateTime(promo.expires_at)}
                    </p>
                  </div>

                  <div className="boxes-list__actions flex shrink-0 items-center gap-1">
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
                        promo.is_active
                          ? {
                              key: "deactivate",
                              label: "Деактивировать",
                              icon: <PowerOff className="size-3.5" />,
                              onClick: () =>
                                activeMutation.mutate({
                                  id: promo.id,
                                  isActive: false,
                                }),
                              danger: true,
                            }
                          : {
                              key: "activate",
                              label: "Активировать",
                              icon: <Power className="size-3.5" />,
                              onClick: () =>
                                activeMutation.mutate({
                                  id: promo.id,
                                  isActive: true,
                                }),
                            },
                      ]}
                    />
                  </div>
                </motion.article>
              ))}
            </div>
          )}

          {showPromos ? (
            <PromoPagination
              page={page}
              pageCount={pageCount}
              total={total}
              pageSize={PROMO_PAGE_SIZE}
              onChange={goToPage}
            />
          ) : null}
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
          <label className="ui-modal__field-label">
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
          <label className="ui-modal__field-label">
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
          <label className="ui-modal__field-label">
            Действует до
            <input
              type="datetime-local"
              value={expiresAt}
              onChange={(e) => setExpiresAt(e.target.value)}
              className={FIELD}
            />
          </label>
          <label className="ui-modal__field-label">
            Лимит использований
            <input
              type="number"
              min={1}
              step={1}
              value={maxUsages}
              onChange={(e) => setMaxUsages(e.target.value)}
              placeholder="Без лимита"
              className={FIELD}
            />
            <span className="mt-1 block text-xs font-normal text-slate-400">
              Оставьте пустым, если ограничение не нужно
            </span>
          </label>
        </form>
      </Modal>
    </PageTransition>
  );
}
