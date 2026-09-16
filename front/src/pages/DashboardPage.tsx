import { Link } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Archive,
  ArchiveRestore,
  ChevronLeft,
  ChevronRight,
  Copy,
  Ellipsis,
  Eye,
  Gift,
  Images,
  LayoutGrid,
  List,
  PencilLine,
  Plus,
  Rocket,
} from "lucide-react";

import { DesignCover } from "../components/DesignCover";
import { PageTransition } from "../components/PageTransition";
import { Spinner } from "../components/Spinner";
import { StatusBadge } from "../components/StatusBadge";
import { useToast } from "../components/Toast";
import { api } from "../lib/api";
import { formatDateTime, pluralize } from "../lib/format";
import type { Box, BoxDesign } from "../lib/types";

type BoxesView = "grid" | "list";

const BOXES_VIEW_STORAGE_KEY = "pixelgift.boxes-view";
const BOXES_PAGE_SIZE = 10;

function resolveInitialBoxesView(): BoxesView {
  if (typeof window === "undefined") return "grid";
  const stored = window.localStorage.getItem(BOXES_VIEW_STORAGE_KEY);
  return stored === "list" || stored === "grid" ? stored : "grid";
}

function BoxCardMenu({
  box,
  publishPending,
  archivePending,
  unarchivePending,
  onPublish,
  onArchive,
  onUnarchive,
}: {
  box: Box;
  publishPending: boolean;
  archivePending: boolean;
  unarchivePending: boolean;
  onPublish: () => void;
  onArchive: () => void;
  onUnarchive: () => void;
}) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

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

  const close = () => setOpen(false);

  return (
    <div ref={rootRef} className="relative ml-auto">
      <button
        type="button"
        className="btn-ghost size-8 px-0 py-0"
        aria-label="Действия с боксом"
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={() => setOpen((value) => !value)}
      >
        <Ellipsis className="size-4" />
      </button>

      {open && (
        <div
          role="menu"
          className="box-card-menu absolute right-0 bottom-full z-20 mb-2 min-w-[11.5rem] overflow-hidden rounded-2xl border border-white/12 bg-ink-950/95 p-1 shadow-2xl shadow-black/40 backdrop-blur-xl"
        >
          {box.status === "active" ||
          box.status === "opened" ||
          box.status === "archived" ? (
            <Link
              role="menuitem"
              to={`/app/boxes/${box.id}`}
              className="box-card-menu__item"
              onClick={close}
            >
              <Eye className="size-3.5" />
              Смотреть
            </Link>
          ) : (
            <Link
              role="menuitem"
              to={`/app/boxes/${box.id}`}
              className="box-card-menu__item"
              onClick={close}
            >
              <PencilLine className="size-3.5" />
              Редактировать
            </Link>
          )}

          {box.status === "draft" && (
            <button
              type="button"
              role="menuitem"
              className="box-card-menu__item"
              disabled={publishPending || box.items.length === 0}
              onClick={() => {
                onPublish();
                close();
              }}
            >
              <Rocket className="size-3.5" />
              Опубликовать
            </button>
          )}

          {box.status !== "archived" && (
            <button
              type="button"
              role="menuitem"
              className="box-card-menu__item box-card-menu__item--danger"
              disabled={archivePending}
              onClick={() => {
                onArchive();
                close();
              }}
            >
              <Archive className="size-3.5" />
              В архив
            </button>
          )}

          {box.status === "archived" && box.first_opened_at == null && (
            <button
              type="button"
              role="menuitem"
              className="box-card-menu__item"
              disabled={unarchivePending}
              onClick={() => {
                onUnarchive();
                close();
              }}
            >
              <ArchiveRestore className="size-3.5" />
              Из архива
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function BoxesViewToggle({
  value,
  onChange,
}: {
  value: BoxesView;
  onChange: (view: BoxesView) => void;
}) {
  return (
    <div
      className="boxes-view-toggle"
      role="group"
      aria-label="Вид списка боксов"
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

function BoxesPagination({
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
      aria-label="Страницы боксов"
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

export function DashboardPage() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [view, setView] = useState<BoxesView>(() => resolveInitialBoxesView());
  const [page, setPage] = useState(1);

  const boxesQuery = useQuery({
    queryKey: ["boxes", page, BOXES_PAGE_SIZE],
    queryFn: () => api.boxes({ page, pageSize: BOXES_PAGE_SIZE }),
  });
  const designsQuery = useQuery({ queryKey: ["designs"], queryFn: api.designs });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["boxes"] });

  const publish = useMutation({
    mutationFn: api.publishBox,
    onSuccess: () => {
      toast("Бокс опубликован — ссылка активна");
      invalidate();
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const archive = useMutation({
    mutationFn: api.archiveBox,
    onSuccess: () => {
      toast("Бокс перемещён в архив");
      invalidate();
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const unarchive = useMutation({
    mutationFn: api.unarchiveBox,
    onSuccess: () => {
      toast("Бокс возвращён из архива");
      invalidate();
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const copyLink = async (box: Box) => {
    const url = `${window.location.origin}/b/${box.public_slug}`;
    try {
      await navigator.clipboard.writeText(url);
      toast("Ссылка скопирована");
    } catch {
      toast(url, "error");
    }
  };

  const setBoxesView = (next: BoxesView) => {
    setView(next);
    window.localStorage.setItem(BOXES_VIEW_STORAGE_KEY, next);
  };

  const designsById = new Map<string, BoxDesign>(
    (designsQuery.data ?? []).map((design) => [design.id, design]),
  );

  const total = boxesQuery.data?.total ?? 0;
  const pageBoxes = boxesQuery.data?.items ?? [];
  const pageCount = Math.max(1, Math.ceil(total / BOXES_PAGE_SIZE));
  const showBoxes = boxesQuery.isSuccess && total > 0;

  useEffect(() => {
    if (page > pageCount) setPage(pageCount);
  }, [page, pageCount]);

  const goToPage = (next: number) => {
    setPage(Math.min(pageCount, Math.max(1, next)));
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <PageTransition>
      <div className="flex flex-wrap items-end justify-between gap-4 pt-12 pb-10">
        <div>
          <h1 className="font-sans text-3xl font-semibold tracking-tight sm:text-4xl">
            Мои боксы
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            {total > 0
              ? `${total} ${pluralize(total, ["бокс", "бокса", "боксов"])} в вашей коллекции`
              : "Здесь появятся ваши подарки"}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2.5">
          {showBoxes ? (
            <BoxesViewToggle value={view} onChange={setBoxesView} />
          ) : null}
          <Link to="/app/boxes/new" className="btn-primary">
            <Plus className="size-4" />
            Новый бокс
          </Link>
        </div>
      </div>

      {boxesQuery.isPending && <Spinner label="Загружаем боксы…" className="py-20" />}

      {boxesQuery.isError && (
        <div className="glass-soft p-8 text-center text-sm text-rose-200">
          Не удалось загрузить боксы: {(boxesQuery.error as Error).message}
        </div>
      )}

      {boxesQuery.isSuccess && total === 0 && (
        <div className="glass flex flex-col items-center px-6 py-16 text-center">
          <span className="grid size-16 place-items-center rounded-3xl bg-glow-violet/15 text-3xl">
            🎁
          </span>
          <h2 className="mt-6 font-sans text-2xl font-semibold">Пока пусто</h2>
          <p className="mt-3 max-w-sm text-sm text-slate-400">
            Соберите первый бокс: выберите оформление, добавьте фото и голосовые, задайте
            дату открытия.
          </p>
          <Link to="/app/boxes/new" className="btn-primary mt-8">
            <Gift className="size-4" />
            Собрать первый бокс
          </Link>
        </div>
      )}

      {showBoxes && view === "grid" && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {pageBoxes.map((box, index) => {
            const design = designsById.get(box.design_id);

            return (
              <motion.article
                key={box.id}
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: Math.min(index, 10) * 0.04 }}
                className="glass relative flex aspect-square flex-col !rounded-xl"
              >
                <DesignCover
                  code={design?.code ?? "romantic"}
                  previewImageUrl={design?.preview_image_url}
                  themeConfig={design?.theme_config}
                  heightClassName="min-h-0 flex-1 rounded-t-xl"
                >
                  <div className="absolute inset-0 flex items-start justify-end p-3">
                    <StatusBadge status={box.status} />
                  </div>
                </DesignCover>

                <div className="flex shrink-0 flex-col gap-2.5 p-3.5 sm:p-4">
                  <div className="min-w-0">
                    <h2 className="truncate font-sans text-base font-semibold sm:text-lg">
                      {box.title}
                    </h2>
                    <p className="mt-0.5 truncate text-xs text-slate-400 sm:text-sm">
                      Для {box.recipient_name} · {formatDateTime(box.activates_at)}
                    </p>
                  </div>

                  <div className="mt-auto flex flex-wrap items-center gap-1.5">
                    <span className="chip px-2 py-0.5">
                      <Images className="size-3.5" />
                      {box.items.length}{" "}
                      {pluralize(box.items.length, ["файл", "файла", "файлов"])}
                    </span>
                    <button
                      type="button"
                      className="btn-ghost px-3 py-1.5 text-xs"
                      onClick={() => copyLink(box)}
                    >
                      <Copy className="size-3.5" />
                      Ссылка
                    </button>
                    <BoxCardMenu
                      box={box}
                      publishPending={publish.isPending}
                      archivePending={archive.isPending}
                      unarchivePending={unarchive.isPending}
                      onPublish={() => publish.mutate(box.id)}
                      onArchive={() => archive.mutate(box.id)}
                      onUnarchive={() => unarchive.mutate(box.id)}
                    />
                  </div>
                </div>
              </motion.article>
            );
          })}
        </div>
      )}

      {showBoxes && view === "list" && (
        <div className="boxes-list flex flex-col gap-2.5">
          {pageBoxes.map((box, index) => {
            const design = designsById.get(box.design_id);

            return (
              <motion.article
                key={box.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: Math.min(index, 10) * 0.03 }}
                className="boxes-list__row glass relative flex items-center gap-3 !rounded-xl p-2.5 sm:gap-4 sm:p-3"
              >
                <Link
                  to={`/app/boxes/${box.id}`}
                  className="boxes-list__cover shrink-0 overflow-hidden rounded-lg"
                  aria-label={`Открыть бокс «${box.title}»`}
                >
                  <DesignCover
                    code={design?.code ?? "romantic"}
                    previewImageUrl={design?.preview_image_url}
                    themeConfig={design?.theme_config}
                    heightClassName="h-[4.5rem] w-[4.5rem] sm:h-16 sm:w-28"
                  />
                </Link>

                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="truncate font-sans text-sm font-semibold sm:text-base">
                      <Link
                        to={`/app/boxes/${box.id}`}
                        className="boxes-list__title transition hover:text-white"
                      >
                        {box.title}
                      </Link>
                    </h2>
                    <StatusBadge status={box.status} />
                  </div>
                  <p className="mt-1 truncate text-xs text-slate-400 sm:text-sm">
                    Для {box.recipient_name} · {formatDateTime(box.activates_at)}
                  </p>
                </div>

                <div className="hidden items-center gap-2 md:flex">
                  <span className="chip px-2 py-0.5">
                    <Images className="size-3.5" />
                    {box.items.length}{" "}
                    {pluralize(box.items.length, ["файл", "файла", "файлов"])}
                  </span>
                </div>

                <div className="flex shrink-0 items-center gap-1">
                  <button
                    type="button"
                    className="btn-ghost hidden px-3 py-1.5 text-xs sm:inline-flex"
                    onClick={() => copyLink(box)}
                  >
                    <Copy className="size-3.5" />
                    Ссылка
                  </button>
                  <button
                    type="button"
                    className="btn-ghost size-8 px-0 py-0 sm:hidden"
                    aria-label="Скопировать ссылку"
                    onClick={() => copyLink(box)}
                  >
                    <Copy className="size-3.5" />
                  </button>
                  <BoxCardMenu
                    box={box}
                    publishPending={publish.isPending}
                    archivePending={archive.isPending}
                    unarchivePending={unarchive.isPending}
                    onPublish={() => publish.mutate(box.id)}
                    onArchive={() => archive.mutate(box.id)}
                    onUnarchive={() => unarchive.mutate(box.id)}
                  />
                </div>
              </motion.article>
            );
          })}
        </div>
      )}

      {showBoxes ? (
        <BoxesPagination
          page={page}
          pageCount={pageCount}
          total={total}
          pageSize={BOXES_PAGE_SIZE}
          onChange={goToPage}
        />
      ) : null}
    </PageTransition>
  );
}
