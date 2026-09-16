import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Archive,
  CalendarDays,
  Gift,
  LayoutGrid,
  LogOut,
  PencilLine,
  Sparkles,
  UserRound,
} from "lucide-react";

import { PageTransition } from "../components/PageTransition";
import { Spinner } from "../components/Spinner";
import { TelegramIcon } from "../components/TelegramIcon";
import { useAuth } from "../hooks/useAuth";
import { api, API_URL } from "../lib/api";
import { formatDateTime, pluralize } from "../lib/format";
import type { CurrentUser } from "../lib/types";

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

export function ProfilePage() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const meQuery = useQuery({ queryKey: ["me"], queryFn: api.me });
  const boxesQuery = useQuery({
    queryKey: ["boxes", "summary"],
    queryFn: () => api.boxes({ page: 1, pageSize: 1 }),
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
            <div
              className="pointer-events-none absolute inset-x-0 -top-24 h-48 opacity-50 blur-3xl"
              style={{
                background:
                  "radial-gradient(circle at 20% 40%, rgb(168 85 247 / 0.35), transparent 55%), radial-gradient(circle at 80% 20%, rgb(34 211 238 / 0.22), transparent 50%)",
              }}
            />

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
                <Link to="/app" className="btn-ghost px-4 py-2.5 text-xs sm:text-sm">
                  <LayoutGrid className="size-4" />
                  Мои боксы
                </Link>
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

        <div className="mt-5 flex flex-wrap gap-3">
          <Link to="/app/boxes/new" className="btn-primary">
            <Gift className="size-4" />
            Собрать новый бокс
          </Link>
          <Link to="/app" className="btn-ghost">
            Перейти к коллекции
          </Link>
          {user.is_admin ? (
            <Link to="/admin" className="btn-ghost">
              <Sparkles className="size-4" />
              Панель
            </Link>
          ) : null}
        </div>
      </div>
    </PageTransition>
  );
}
