import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowDownWideNarrow,
  ArrowLeft,
  ArrowUpWideNarrow,
  Check,
  ChevronLeft,
  ChevronRight,
  Filter,
  Headphones,
  Image as ImageIcon,
} from "lucide-react";

import { PageTransition } from "../components/PageTransition";
import { Spinner } from "../components/Spinner";
import { useToast } from "../components/Toast";
import { api, supportAttachmentUrl } from "../lib/api";
import { formatDateTime } from "../lib/format";
import type { SupportTicket, SupportTicketStatus } from "../lib/types";

const PAGE_SIZE = 10;

const STATUS_LABELS: Record<SupportTicketStatus, string> = {
  new: "Новое",
  in_progress: "В работе",
  resolved: "Решено",
  closed: "Закрыто",
};

const STATUS_OPTIONS = Object.entries(STATUS_LABELS) as [
  SupportTicketStatus,
  string,
][];

type StatusFilter = SupportTicketStatus | "all";
type SortOrder = "asc" | "desc";

function ticketsWord(count: number) {
  const mod10 = count % 10;
  const mod100 = count % 100;
  if (mod10 === 1 && mod100 !== 11) return "обращение";
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return "обращения";
  return "обращений";
}

export function AdminSupportPage() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [sort, setSort] = useState<SortOrder>("desc");
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const ticketsQuery = useQuery({
    queryKey: ["admin-support", statusFilter, sort, page, PAGE_SIZE],
    queryFn: () =>
      api.adminSupportTickets({
        status: statusFilter === "all" ? null : statusFilter,
        sort,
        page,
        pageSize: PAGE_SIZE,
      }),
  });

  const patchMutation = useMutation({
    mutationFn: ({
      id,
      status,
    }: {
      id: string;
      status: SupportTicketStatus;
    }) => api.patchSupportTicketStatus(id, status),
    onSuccess: (ticket) => {
      void queryClient.invalidateQueries({ queryKey: ["admin-support"] });
      toast(`Статус: ${STATUS_LABELS[ticket.status]}`, "success");
    },
    onError: (error) => {
      toast((error as Error).message, "error");
    },
  });

  const tickets = ticketsQuery.data?.items ?? [];
  const total = ticketsQuery.data?.total ?? 0;
  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  useEffect(() => {
    if (page > pageCount) setPage(pageCount);
  }, [page, pageCount]);

  const selected = useMemo(
    () => tickets.find((ticket) => ticket.id === selectedId) ?? tickets[0] ?? null,
    [tickets, selectedId],
  );

  if (ticketsQuery.isPending) {
    return <Spinner label="Загружаем обращения…" className="py-32" />;
  }

  if (ticketsQuery.isError) {
    return (
      <PageTransition>
        <div className="glass-soft mt-16 p-8 text-center text-sm text-rose-200">
          {(ticketsQuery.error as Error).message}
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="pt-10 pb-8 sm:pt-14">
        <Link
          to="/admin"
          className="btn-ghost inline-flex items-center gap-2 px-3 py-2 text-sm"
        >
          <ArrowLeft className="size-4" />
          К панели
        </Link>

        <div className="mt-5 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="chip w-fit">
              <Headphones className="size-3.5" />
              Поддержка
            </p>
            <h1 className="mt-3 font-sans text-2xl font-semibold tracking-tight sm:text-3xl">
              Обращения
            </h1>
            <p className="mt-2 text-sm text-slate-400">
              {total} {ticketsWord(total)}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              className="btn-ghost size-9 px-0 py-0"
              aria-label={
                sort === "desc"
                  ? "Сортировка: сначала новые"
                  : "Сортировка: сначала старые"
              }
              title={
                sort === "desc"
                  ? "Сначала новые — нажмите для старых"
                  : "Сначала старые — нажмите для новых"
              }
              onClick={() => {
                setSort((value) => (value === "desc" ? "asc" : "desc"));
                setPage(1);
                setSelectedId(null);
              }}
            >
              {sort === "desc" ? (
                <ArrowDownWideNarrow className="size-4" />
              ) : (
                <ArrowUpWideNarrow className="size-4" />
              )}
            </button>

            <StatusFilterMenu
              value={statusFilter}
              onChange={(value) => {
                setStatusFilter(value);
                setPage(1);
                setSelectedId(null);
              }}
            />
          </div>
        </div>

        {total === 0 ? (
          <div className="glass mt-10 p-10 text-center text-sm text-slate-400">
            Пока нет обращений
          </div>
        ) : (
          <>
            <div className="mt-8 grid gap-4 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.15fr)]">
              <div className="space-y-2">
                {tickets.map((ticket, index) => (
                  <motion.button
                    key={ticket.id}
                    type="button"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.03 }}
                    onClick={() => setSelectedId(ticket.id)}
                    className={`glass-soft w-full p-4 text-left transition ${
                      selected?.id === ticket.id
                        ? "border-glow-violet/40 bg-glow-violet/10"
                        : "hover:border-white/20"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <h2 className="line-clamp-1 text-sm font-semibold text-slate-100">
                        {ticket.subject}
                      </h2>
                      <StatusPill status={ticket.status} />
                    </div>
                    <p className="mt-1 truncate text-xs text-slate-500">
                      {ticket.contact} · {formatDateTime(ticket.created_at)}
                    </p>
                  </motion.button>
                ))}
              </div>

              {selected ? (
                <TicketDetail
                  ticket={selected}
                  busy={patchMutation.isPending}
                  onStatusChange={(status) =>
                    patchMutation.mutate({ id: selected.id, status })
                  }
                />
              ) : null}
            </div>

            <TicketsPagination
              page={page}
              pageCount={pageCount}
              total={total}
              pageSize={PAGE_SIZE}
              onChange={(next) => {
                setPage(Math.min(pageCount, Math.max(1, next)));
                setSelectedId(null);
              }}
            />
          </>
        )}
      </div>
    </PageTransition>
  );
}

function StatusFilterMenu({
  value,
  onChange,
}: {
  value: StatusFilter;
  onChange: (value: StatusFilter) => void;
}) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const active = value !== "all";

  useEffect(() => {
    if (!open) return;

    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node | null;
      if (!target || rootRef.current?.contains(target)) return;
      setOpen(false);
    };

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    window.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("pointerdown", onPointerDown);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const options: { value: StatusFilter; label: string }[] = [
    { value: "all", label: "Все" },
    ...STATUS_OPTIONS.map(([status, label]) => ({ value: status, label })),
  ];

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        className={`btn-ghost size-9 px-0 py-0 ${
          active ? "border-glow-violet/40 text-glow-violet" : ""
        }`}
        aria-label="Фильтр по статусу"
        aria-expanded={open}
        aria-haspopup="menu"
        title={
          active
            ? `Статус: ${STATUS_LABELS[value as SupportTicketStatus]}`
            : "Фильтр по статусу"
        }
        onClick={() => setOpen((current) => !current)}
      >
        <Filter className="size-4" />
      </button>

      {open ? (
        <div
          role="menu"
          className="absolute right-0 z-20 mt-2 min-w-[10.5rem] overflow-hidden rounded-2xl border border-white/12 bg-ink-950/95 p-1 shadow-2xl shadow-black/40 backdrop-blur-xl"
        >
          {options.map((option) => {
            const selected = option.value === value;
            return (
              <button
                key={option.value}
                type="button"
                role="menuitemradio"
                aria-checked={selected}
                className={`flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm transition ${
                  selected
                    ? "bg-glow-violet/15 text-slate-100"
                    : "text-slate-300 hover:bg-white/5 hover:text-slate-100"
                }`}
                onClick={() => {
                  onChange(option.value);
                  setOpen(false);
                }}
              >
                <span className="flex-1">{option.label}</span>
                {selected ? <Check className="size-3.5 shrink-0" /> : null}
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}

function TicketsPagination({
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
      className="mt-6 flex flex-wrap items-center justify-between gap-3"
      aria-label="Страницы обращений"
    >
      <p className="text-sm text-slate-400">
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
        <span className="min-w-[4.5rem] text-center text-sm tabular-nums text-slate-300">
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

function StatusPill({ status }: { status: SupportTicketStatus }) {
  return (
    <span
      className={`status-badge status-badge--${
        status === "new"
          ? "scheduled"
          : status === "in_progress"
            ? "active"
            : status === "resolved"
              ? "opened"
              : "archived"
      }`}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}

function TicketDetail({
  ticket,
  busy,
  onStatusChange,
}: {
  ticket: SupportTicket;
  busy: boolean;
  onStatusChange: (status: SupportTicketStatus) => void;
}) {
  return (
    <div className="glass p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-sans text-lg font-semibold text-slate-100">
            {ticket.subject}
          </h2>
          <p className="mt-1 text-sm text-slate-400">{ticket.contact}</p>
          <p className="mt-1 text-xs text-slate-500">
            {formatDateTime(ticket.created_at)}
          </p>
        </div>
        <label className="text-xs text-slate-400">
          Статус
          <select
            className="field mt-1 py-2 text-sm"
            value={ticket.status}
            disabled={busy}
            onChange={(event) =>
              onStatusChange(event.target.value as SupportTicketStatus)
            }
          >
            {STATUS_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <p className="mt-5 whitespace-pre-wrap text-sm leading-relaxed text-slate-300">
        {ticket.description}
      </p>

      {ticket.attachments.length > 0 ? (
        <div className="mt-6">
          <p className="mb-3 inline-flex items-center gap-1.5 text-xs font-semibold tracking-wide text-slate-500 uppercase">
            <ImageIcon className="size-3.5" />
            Вложения
          </p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {ticket.attachments.map((attachment) => (
              <a
                key={attachment.id}
                href={supportAttachmentUrl(ticket.id, attachment.id)}
                target="_blank"
                rel="noreferrer"
                className="overflow-hidden rounded-2xl border border-white/10 bg-black/30"
              >
                <img
                  src={supportAttachmentUrl(ticket.id, attachment.id)}
                  alt={attachment.original_filename ?? "Вложение"}
                  className="aspect-square w-full object-cover"
                  loading="lazy"
                />
              </a>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
