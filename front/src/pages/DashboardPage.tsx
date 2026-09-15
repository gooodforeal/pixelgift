import { Link } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Archive,
  ArchiveRestore,
  Copy,
  Ellipsis,
  Eye,
  Gift,
  Images,
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

export function DashboardPage() {
  const toast = useToast();
  const queryClient = useQueryClient();

  const boxesQuery = useQuery({ queryKey: ["boxes"], queryFn: api.boxes });
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

  const designsById = new Map<string, BoxDesign>(
    (designsQuery.data ?? []).map((design) => [design.id, design]),
  );

  const boxes = boxesQuery.data ?? [];

  return (
    <PageTransition>
      <div className="flex flex-wrap items-end justify-between gap-4 pt-12 pb-10">
        <div>
          <h1 className="font-sans font-semibold text-3xl tracking-tight sm:text-4xl">Мои боксы</h1>
          <p className="mt-2 text-sm text-slate-400">
            {boxes.length > 0
              ? `${boxes.length} ${pluralize(boxes.length, ["бокс", "бокса", "боксов"])} в вашей коллекции`
              : "Здесь появятся ваши подарки"}
          </p>
        </div>
        <Link to="/app/boxes/new" className="btn-primary">
          <Plus className="size-4" />
          Новый бокс
        </Link>
      </div>

      {boxesQuery.isPending && <Spinner label="Загружаем боксы…" className="py-20" />}

      {boxesQuery.isError && (
        <div className="glass-soft p-8 text-center text-sm text-rose-200">
          Не удалось загрузить боксы: {(boxesQuery.error as Error).message}
        </div>
      )}

      {boxesQuery.isSuccess && boxes.length === 0 && (
        <div className="glass flex flex-col items-center px-6 py-16 text-center">
          <span className="grid size-16 place-items-center rounded-3xl bg-glow-violet/15 text-3xl">
            🎁
          </span>
          <h2 className="font-sans font-semibold mt-6 text-2xl">Пока пусто</h2>
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

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {boxes.map((box, index) => {
          const design = designsById.get(box.design_id);

          return (
            <motion.article
              key={box.id}
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
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
    </PageTransition>
  );
}
