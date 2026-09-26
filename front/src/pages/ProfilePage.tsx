import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Archive,
  ArrowLeftRight,
  Bell,
  CalendarDays,
  CreditCard,
  Gift,
  LogOut,
  PencilLine,
  ShoppingCart,
  Sparkles,
  UserRound,
  Wallet,
} from "lucide-react";

import { PageTransition } from "../components/PageTransition";
import { Spinner } from "../components/Spinner";
import { TelegramIcon } from "../components/TelegramIcon";
import { ToggleSwitch } from "../components/ToggleSwitch";
import { useAuth } from "../hooks/useAuth";
import { api, API_URL } from "../lib/api";
import { formatDateTime, pluralize } from "../lib/format";
import type { CurrentUser, OrderStatus } from "../lib/types";

function displayName(user: CurrentUser): string {
  const parts = [user.first_name, user.last_name].filter(Boolean);
  return parts.join(" ") || "Пользователь";
}

function initials(user: CurrentUser): string {
  const first = user.first_name?.trim().charAt(0) ?? "";
  const last = user.last_name?.trim().charAt(0) ?? "";
  return (first + last || "?").toUpperCase();
}

function avatarUrl(user: CurrentUser): string | null {
  if (!user.photo_url) return null;
  if (user.photo_url.startsWith("http://") || user.photo_url.startsWith("https://")) {
    return user.photo_url;
  }
  return `${API_URL}${user.photo_url.startsWith("/") ? "" : "/"}${user.photo_url}`;
}

function formatMoney(kopecks: number, currency: string): string {
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

const ORDER_STATUS_LABEL: Record<OrderStatus, string> = {
  pending: "Ожидает оплаты",
  succeeded: "Оплачен",
  canceled: "Отменён",
};

function PaymentStatusBadge({ status }: { status: OrderStatus }) {
  return (
    <span className={`status-badge status-badge--${status}`}>
      {ORDER_STATUS_LABEL[status]}
    </span>
  );
}

const BALANCE_REASON_LABEL: Record<string, string> = {
  purchase: "Покупка",
  consume: "Списание",
  refund: "Возврат",
  admin: "Админ",
};

export function ProfilePage() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [logsPage, setLogsPage] = useState(1);
  const [ordersPage, setOrdersPage] = useState(1);

  const syncOrdersQuery = useQuery({
    queryKey: ["orders", "sync"],
    queryFn: async () => {
      const result = await api.syncPendingOrders();
      if (result.synced > 0) {
        await queryClient.invalidateQueries({ queryKey: ["balances"] });
        await queryClient.invalidateQueries({ queryKey: ["balance-logs"] });
        await queryClient.invalidateQueries({ queryKey: ["orders", "list"] });
      }
      return result;
    },
    staleTime: 0,
    refetchOnWindowFocus: true,
  });

  const meQuery = useQuery({ queryKey: ["me"], queryFn: api.me });
  const boxesQuery = useQuery({
    queryKey: ["boxes", "summary"],
    queryFn: () => api.boxes({ page: 1, pageSize: 1 }),
  });
  const balancesQuery = useQuery({
    queryKey: ["balances"],
    queryFn: api.balances,
    enabled: syncOrdersQuery.isFetched,
  });
  const logsQuery = useQuery({
    queryKey: ["balance-logs", logsPage],
    queryFn: () => api.balanceLogs({ page: logsPage, pageSize: 10 }),
    enabled: syncOrdersQuery.isFetched,
  });
  const ordersQuery = useQuery({
    queryKey: ["orders", "list", ordersPage],
    queryFn: () => api.orders({ page: ordersPage, pageSize: 10 }),
    enabled: syncOrdersQuery.isFetched,
  });

  const notificationsMutation = useMutation({
    mutationFn: (notifications_enabled: boolean) =>
      api.updateMe({ notifications_enabled }),
    onSuccess: (updated) => {
      queryClient.setQueryData<CurrentUser>(["me"], updated);
    },
  });

  const user = meQuery.data;
  const total = boxesQuery.data?.total ?? 0;
  const counts = boxesQuery.data?.status_counts ?? {};
  const drafts = counts.draft ?? 0;
  const scheduled = counts.scheduled ?? 0;
  const active = counts.active ?? 0;
  const opened = counts.opened ?? 0;
  const archived = counts.archived ?? 0;
  const photoSrc = user ? avatarUrl(user) : null;
  if (meQuery.isPending) {
    return <Spinner label="Загружаем профиль…" className="py-32" />;
  }

  if (meQuery.isError || !user) {
    return (
      <PageTransition>
        <div className="glass-soft mt-16 p-8 text-center text-sm text-rose-200">
          Не удалось загрузить профиль: {(meQuery.error as Error)?.message ?? "ошибка"}
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="pt-10 pb-6 sm:pt-14">
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass overflow-hidden"
        >
          <div className="relative px-5 py-8 sm:px-8 sm:py-10">
            <div className="relative flex flex-col gap-6 sm:flex-row sm:items-center">
              <div className="relative w-fit shrink-0 self-start">
                {photoSrc ? (
                  <img
                    src={photoSrc}
                    alt=""
                    className="size-20 rounded-3xl object-cover shadow-lg shadow-black/25 sm:size-24"
                    onError={(event) => {
                      event.currentTarget.style.display = "none";
                      const fallback = event.currentTarget.nextElementSibling;
                      if (fallback instanceof HTMLElement) {
                        fallback.style.display = "grid";
                      }
                    }}
                  />
                ) : null}
                <div
                  className="grid size-20 place-items-center rounded-3xl bg-gradient-to-br from-glow-pink via-glow-violet to-glow-cyan text-2xl font-bold text-ink-950 shadow-lg shadow-glow-violet/30 sm:size-24 sm:text-3xl"
                  style={photoSrc ? { display: "none" } : undefined}
                >
                  {initials(user)}
                </div>
                <span className="absolute -right-1 -bottom-1 grid size-8 place-items-center rounded-full border border-white/20 bg-ink-950/80 text-sky-300 shadow-md backdrop-blur">
                  <TelegramIcon className="size-4" />
                </span>
              </div>

              <div className="min-w-0 flex-1">
                <p className="chip w-fit">
                  <UserRound className="size-3.5 text-glow-cyan" />
                  Профиль
                </p>
                <h1 className="mt-3 truncate font-sans text-2xl font-semibold tracking-tight sm:text-3xl">
                  {displayName(user)}
                </h1>
                <p className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-slate-400">
                  {user.username ? (
                    <span className="inline-flex items-center gap-1.5">
                      <TelegramIcon className="size-3.5 text-sky-400" />
                      @{user.username}
                    </span>
                  ) : (
                    <span>Аккаунт Telegram</span>
                  )}
                  {user.language_code ? (
                    <span className="uppercase opacity-80">{user.language_code}</span>
                  ) : null}
                </p>
              </div>

              <div className="flex flex-wrap gap-2 sm:justify-end">
                <button
                  type="button"
                  className="btn-ghost px-4 py-2.5 text-xs sm:text-sm"
                  onClick={() => {
                    void logout().then(() => navigate("/"));
                  }}
                >
                  <LogOut className="size-4" />
                  Выйти
                </button>
              </div>
            </div>
          </div>
        </motion.section>

        <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="glass-soft p-5">
            <div className="flex items-center gap-2 text-xs font-semibold tracking-wide text-slate-400 uppercase">
              <Gift className="size-3.5 text-glow-violet" />
              Всего подарков
            </div>
            <p className="mt-3 font-sans text-3xl font-semibold tabular-nums">
              {boxesQuery.isPending ? "…" : total}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              {boxesQuery.isPending
                ? "Считаем…"
                : `${pluralize(total, ["бокс", "бокса", "боксов"])} в коллекции`}
            </p>
          </div>

          <div className="glass-soft p-5">
            <div className="flex items-center gap-2 text-xs font-semibold tracking-wide text-slate-400 uppercase">
              <PencilLine className="size-3.5 text-slate-300" />
              Черновики
            </div>
            <p className="mt-3 font-sans text-3xl font-semibold tabular-nums">
              {boxesQuery.isPending ? "…" : drafts}
            </p>
          </div>

          <div className="glass-soft p-5">
            <div className="flex items-center gap-2 text-xs font-semibold tracking-wide text-slate-400 uppercase">
              <Sparkles className="size-3.5 text-glow-gold" />
              В пути
            </div>
            <p className="mt-3 font-sans text-3xl font-semibold tabular-nums">
              {boxesQuery.isPending ? "…" : scheduled + active}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              {scheduled} запланировано · {active} ждут открытия
            </p>
            <p className="mt-1 text-xs text-slate-500">{opened} уже открыли</p>
          </div>

          <div className="glass-soft p-5">
            <div className="flex items-center gap-2 text-xs font-semibold tracking-wide text-slate-400 uppercase">
              <Archive className="size-3.5 text-slate-300" />
              Архив
            </div>
            <p className="mt-3 font-sans text-3xl font-semibold tabular-nums">
              {boxesQuery.isPending ? "…" : archived}
            </p>
          </div>
        </div>

        <section className="glass mt-5 overflow-hidden p-5 sm:p-6">
          <h2 className="font-sans text-lg font-semibold">Личные данные</h2>
          <dl className="mt-5 grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="label mb-1.5">Имя</dt>
              <dd className="text-sm text-slate-200">{user.first_name}</dd>
            </div>
            <div>
              <dt className="label mb-1.5">Фамилия</dt>
              <dd className="text-sm text-slate-200">{user.last_name || "—"}</dd>
            </div>
            <div>
              <dt className="label mb-1.5">Telegram</dt>
              <dd className="text-sm text-slate-200">
                {user.username ? `@${user.username}` : "без username"}
              </dd>
            </div>
            <div>
              <dt className="label mb-1.5">Язык</dt>
              <dd className="text-sm text-slate-200">
                {user.language_code?.toUpperCase() || "—"}
              </dd>
            </div>
            <div>
              <dt className="label mb-1.5 inline-flex items-center gap-1.5">
                <CalendarDays className="size-3.5" />
                С нами с
              </dt>
              <dd className="text-sm text-slate-200">{formatDateTime(user.created_at)}</dd>
            </div>
            <div>
              <dt className="label mb-1.5">Последний визит</dt>
              <dd className="text-sm text-slate-200">
                {user.last_seen_at ? formatDateTime(user.last_seen_at) : "—"}
              </dd>
            </div>
          </dl>
        </section>

        <section className="glass mt-5 overflow-hidden p-5 sm:p-6">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 grid size-9 shrink-0 place-items-center rounded-2xl border border-white/10 bg-white/[0.04] text-sky-300">
              <Bell className="size-4" />
            </span>
            <div className="min-w-0 flex-1">
              <h2 className="font-sans text-lg font-semibold">Уведомления</h2>
              <p className="mt-1 text-sm text-slate-400">
                Сообщения в Telegram о публикации, доставке и открытии ваших боксов.
              </p>
              <div className="mt-4">
                <ToggleSwitch
                  checked={user.notifications_enabled}
                  disabled={notificationsMutation.isPending}
                  label={
                    user.notifications_enabled
                      ? "Уведомления включены"
                      : "Уведомления выключены"
                  }
                  onChange={(enabled) => notificationsMutation.mutate(enabled)}
                />
              </div>
              {notificationsMutation.isError ? (
                <p className="mt-3 text-sm text-rose-300" role="alert">
                  Не удалось сохранить настройку:{" "}
                  {(notificationsMutation.error as Error)?.message ?? "ошибка"}
                </p>
              ) : null}
            </div>
          </div>
        </section>

        <section className="glass mt-5 overflow-hidden p-5 sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="inline-flex items-center gap-2 font-sans text-lg font-semibold">
                <Wallet className="size-5 text-glow-cyan" />
                Доступные балансы
              </h2>
              <p className="mt-1 text-sm text-slate-400">
                Остатки по купленным товарам. 1 кредит = 1 новый бокс.
              </p>
            </div>
            <Link to="/products" className="btn-primary text-xs sm:text-sm">
              <ShoppingCart className="size-4" />
              Купить
            </Link>
          </div>
          {balancesQuery.isPending ? (
            <p className="mt-4 text-sm text-slate-500">Загружаем…</p>
          ) : balancesQuery.isError ? (
            <p className="mt-4 text-sm text-rose-300">Не удалось загрузить балансы</p>
          ) : !(balancesQuery.data?.length ?? 0) ? (
            <p className="mt-4 text-sm text-slate-400">
              Пока пусто. Купите боксы, чтобы публиковать подарки.
            </p>
          ) : (
            <ul className="mt-4 divide-y divide-white/5 rounded-2xl border border-white/10">
              {balancesQuery.data!.map((item) => (
                <li
                  key={item.product_id}
                  className="flex items-center justify-between gap-4 px-4 py-3"
                >
                  <p className="min-w-0 truncate text-sm font-medium text-slate-100">
                    {item.name}
                  </p>
                  <p className="shrink-0 font-sans text-lg font-semibold tabular-nums text-slate-100">
                    {item.balance}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="glass mt-5 overflow-hidden p-5 sm:p-6">
          <h2 className="inline-flex items-center gap-2 font-sans text-lg font-semibold">
            <ArrowLeftRight className="size-5 text-glow-gold" />
            Изменения балансов
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Начисления и списания по товарам.
          </p>
          {logsQuery.isPending ? (
            <p className="mt-4 text-sm text-slate-500">Загружаем…</p>
          ) : logsQuery.isError ? (
            <p className="mt-4 text-sm text-rose-300">Не удалось загрузить изменения</p>
          ) : !(logsQuery.data?.items.length ?? 0) ? (
            <p className="mt-4 text-sm text-slate-400">Записей пока нет.</p>
          ) : (
            <>
              <div className="mt-4 overflow-x-auto">
                <table className="w-full min-w-[32rem] text-left text-sm">
                  <thead className="text-xs tracking-wide text-slate-500 uppercase">
                    <tr>
                      <th className="pb-2 font-medium">Дата</th>
                      <th className="pb-2 font-medium">Товар</th>
                      <th className="pb-2 font-medium">Δ</th>
                      <th className="pb-2 font-medium">Тип</th>
                      <th className="pb-2 font-medium">После</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {logsQuery.data!.items.map((row) => (
                      <tr key={row.id}>
                        <td className="py-2.5 pr-3 text-slate-400 whitespace-nowrap">
                          {formatDateTime(row.created_at)}
                        </td>
                        <td className="py-2.5 pr-3 text-slate-200">{row.name}</td>
                        <td
                          className={`py-2.5 pr-3 tabular-nums ${
                            row.delta > 0 ? "text-emerald-300" : "text-rose-300"
                          }`}
                        >
                          {row.delta > 0 ? `+${row.delta}` : row.delta}
                        </td>
                        <td className="py-2.5 pr-3 text-slate-400">
                          {BALANCE_REASON_LABEL[row.reason] ?? row.reason}
                        </td>
                        <td className="py-2.5 tabular-nums text-slate-200">
                          {row.balance_after}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {logsQuery.data!.total > logsQuery.data!.page_size ? (
                <div className="mt-4 flex items-center justify-between gap-3">
                  <button
                    type="button"
                    className="btn-ghost text-xs"
                    disabled={logsPage <= 1}
                    onClick={() => setLogsPage((p) => Math.max(1, p - 1))}
                  >
                    Назад
                  </button>
                  <span className="text-xs text-slate-500">
                    Стр. {logsQuery.data!.page} · всего {logsQuery.data!.total}
                  </span>
                  <button
                    type="button"
                    className="btn-ghost text-xs"
                    disabled={
                      logsPage * logsQuery.data!.page_size >= logsQuery.data!.total
                    }
                    onClick={() => setLogsPage((p) => p + 1)}
                  >
                    Вперёд
                  </button>
                </div>
              ) : null}
            </>
          )}
        </section>

        <section className="glass mt-5 overflow-hidden p-5 sm:p-6">
          <h2 className="inline-flex items-center gap-2 font-sans text-lg font-semibold">
            <CreditCard className="size-5 text-glow-violet" />
            Платежи
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Заказы и оплата через ЮKassa.
          </p>
          {ordersQuery.isPending ? (
            <p className="mt-4 text-sm text-slate-500">Загружаем…</p>
          ) : ordersQuery.isError ? (
            <p className="mt-4 text-sm text-rose-300">Не удалось загрузить платежи</p>
          ) : !(ordersQuery.data?.items.length ?? 0) ? (
            <p className="mt-4 text-sm text-slate-400">Платежей пока нет.</p>
          ) : (
            <>
              <div className="mt-4 overflow-x-auto">
                <table className="w-full min-w-[36rem] text-left text-sm">
                  <thead className="text-xs tracking-wide text-slate-500 uppercase">
                    <tr>
                      <th className="pb-2 font-medium">Дата</th>
                      <th className="pb-2 font-medium">Сумма</th>
                      <th className="pb-2 font-medium">Позиции</th>
                      <th className="pb-2 font-medium">Статус</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {ordersQuery.data!.items.map((order) => {
                      const itemsCount = order.items.reduce(
                        (sum, item) => sum + item.quantity,
                        0,
                      );
                      return (
                        <tr key={order.id}>
                          <td className="py-2.5 pr-3 text-slate-400 whitespace-nowrap">
                            {formatDateTime(order.created_at)}
                          </td>
                          <td className="py-2.5 pr-3">
                            <span className="tabular-nums text-slate-100">
                              {formatMoney(order.amount, order.currency)}
                            </span>
                            {order.discount_percent ? (
                              <span className="mt-0.5 block text-xs text-emerald-300/90">
                                −{order.discount_percent}%
                                {order.amount_before_discount != null
                                  ? ` с ${formatMoney(
                                      order.amount_before_discount,
                                      order.currency,
                                    )}`
                                  : ""}
                              </span>
                            ) : null}
                          </td>
                          <td className="py-2.5 pr-3 text-slate-400">
                            {itemsCount}{" "}
                            {pluralize(itemsCount, [
                              "позиция",
                              "позиции",
                              "позиций",
                            ])}
                          </td>
                          <td className="py-2.5">
                            <PaymentStatusBadge status={order.status} />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              {ordersQuery.data!.total > ordersQuery.data!.page_size ? (
                <div className="mt-4 flex items-center justify-between gap-3">
                  <button
                    type="button"
                    className="btn-ghost text-xs"
                    disabled={ordersPage <= 1}
                    onClick={() => setOrdersPage((p) => Math.max(1, p - 1))}
                  >
                    Назад
                  </button>
                  <span className="text-xs text-slate-500">
                    Стр. {ordersQuery.data!.page} · всего {ordersQuery.data!.total}
                  </span>
                  <button
                    type="button"
                    className="btn-ghost text-xs"
                    disabled={
                      ordersPage * ordersQuery.data!.page_size >=
                      ordersQuery.data!.total
                    }
                    onClick={() => setOrdersPage((p) => p + 1)}
                  >
                    Вперёд
                  </button>
                </div>
              ) : null}
            </>
          )}
        </section>
      </div>
    </PageTransition>
  );
}
