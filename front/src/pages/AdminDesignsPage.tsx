import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { ArrowLeft, Pencil, Plus, Palette } from "lucide-react";

import { DesignCover } from "../components/DesignCover";
import { PageTransition } from "../components/PageTransition";
import { Spinner } from "../components/Spinner";
import { ToggleSwitch } from "../components/ToggleSwitch";
import { api } from "../lib/api";
import type { AdminBoxDesign } from "../lib/types";

export function AdminDesignsPage() {
  const queryClient = useQueryClient();
  const designsQuery = useQuery({
    queryKey: ["admin-designs"],
    queryFn: api.adminDesigns,
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      api.patchAdminDesign(id, { is_active }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-designs"] });
      void queryClient.invalidateQueries({ queryKey: ["designs"] });
    },
  });

  if (designsQuery.isPending) {
    return <Spinner label="Загружаем дизайны…" className="py-32" />;
  }

  if (designsQuery.isError) {
    return (
      <PageTransition>
        <div className="glass-soft mt-16 p-8 text-center text-sm text-rose-200">
          {(designsQuery.error as Error).message}
        </div>
      </PageTransition>
    );
  }

  const designs = designsQuery.data ?? [];

  return (
    <PageTransition>
      <div className="pt-10 pb-6 sm:pt-14">
        <Link
          to="/admin"
          className="btn-ghost inline-flex items-center gap-2 px-3 py-2 text-sm"
        >
          <ArrowLeft className="size-4" />
          К панели
        </Link>
        <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="chip w-fit">
              <Palette className="size-3.5" />
              Админ
            </p>
            <h1 className="mt-3 font-sans text-2xl font-semibold tracking-tight sm:text-3xl">
              Дизайны коробок
            </h1>
            <p className="mt-2 max-w-xl text-sm text-slate-400">
              Создавайте темы, палитры и превью. Неактивные скрыты из выбора у пользователей.
            </p>
          </div>
          <Link to="/admin/designs/new" className="btn-primary">
            <Plus className="size-4" />
            Новый дизайн
          </Link>
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {designs.map((design, index) => (
            <DesignCard
              key={design.id}
              design={design}
              index={index}
              busy={toggleMutation.isPending}
              onToggle={(is_active) =>
                toggleMutation.mutate({ id: design.id, is_active })
              }
            />
          ))}
        </div>
      </div>
    </PageTransition>
  );
}

function DesignCard({
  design,
  index,
  busy,
  onToggle,
}: {
  design: AdminBoxDesign;
  index: number;
  busy: boolean;
  onToggle: (is_active: boolean) => void;
}) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      className="glass overflow-hidden !rounded-xl"
    >
      <DesignCover
        code={design.code}
        previewImageUrl={design.preview_image_url}
        themeConfig={design.theme_config}
        heightClassName="h-36"
      />
      <div className="space-y-3 p-4">
        <div>
          <h2 className="font-sans text-base font-semibold">{design.name}</h2>
          <p className="mt-0.5 text-xs text-slate-400">
            {design.code} · порядок {design.sort_order}
          </p>
        </div>
        <div className="flex items-center justify-between gap-3">
          <ToggleSwitch
            checked={design.is_active}
            disabled={busy}
            label="Активен"
            onChange={onToggle}
          />
          <Link
            to={`/admin/designs/${design.id}`}
            className="btn-ghost inline-flex items-center gap-1.5 px-3 py-2 text-sm"
          >
            <Pencil className="size-3.5" />
            Править
          </Link>
        </div>
      </div>
    </motion.article>
  );
}
