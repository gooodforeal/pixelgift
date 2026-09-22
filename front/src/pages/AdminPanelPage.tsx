import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { BarChart3, Database, Headphones, Palette, Shield } from "lucide-react";

import { PageTransition } from "../components/PageTransition";

type PanelSection = {
  to?: string;
  title: string;
  description: string;
  icon: typeof Palette;
  external?: boolean;
  soon?: boolean;
};

const SECTIONS: PanelSection[] = [
  {
    to: "/app/panel/designs",
    title: "Дизайны",
    description: "Темы коробок, палитры, обложки и активность.",
    icon: Palette,
  },
  {
    to: "/app/panel/support",
    title: "Поддержка",
    description: "Обращения пользователей и смена статусов.",
    icon: Headphones,
  },
  {
    to: "/admin",
    title: "Админка",
    description: "SQLAdmin: пользователи, боксы, уведомления и остальные таблицы.",
    icon: Database,
    external: true,
  },
  {
    title: "Аналитика",
    description: "Дашборды и метрики в Apache Superset — скоро.",
    icon: BarChart3,
    soon: true,
  },
];

export function AdminPanelPage() {
  return (
    <PageTransition>
      <div className="pt-10 pb-6 sm:pt-14">
        <p className="chip w-fit">
          <Shield className="size-3.5" />
          Панель
        </p>
        <h1 className="mt-3 font-sans text-2xl font-semibold tracking-tight sm:text-3xl">
          Панель
        </h1>
        <p className="mt-2 max-w-xl text-sm text-slate-400">
          Управление продуктом. Сюда будут добавляться новые разделы.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {SECTIONS.map((section, index) => {
            const body = (
              <>
                <div className="flex items-start justify-between gap-3">
                  <span className="grid size-11 place-items-center rounded-2xl border border-white/10 bg-white/[0.05] text-glow-cyan transition group-hover:border-glow-violet/40 group-hover:text-glow-violet">
                    <section.icon className="size-5" />
                  </span>
                  {section.soon ? (
                    <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-0.5 text-[11px] font-medium tracking-wide text-slate-400 uppercase">
                      Скоро
                    </span>
                  ) : null}
                </div>
                <div>
                  <h2 className="font-sans text-base font-semibold text-slate-100">
                    {section.title}
                  </h2>
                  <p className="mt-1.5 text-sm leading-relaxed text-slate-400">
                    {section.description}
                  </p>
                </div>
              </>
            );
            const className =
              "glass group flex h-full flex-col gap-3 p-5 transition hover:border-white/20 sm:p-6";
            return (
              <motion.div
                key={section.title}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.04 }}
              >
                {section.soon ? (
                  <div
                    className={`${className} cursor-default opacity-80`}
                    aria-disabled="true"
                  >
                    {body}
                  </div>
                ) : section.external ? (
                  <a href={section.to} className={className}>
                    {body}
                  </a>
                ) : (
                  <Link to={section.to!} className={className}>
                    {body}
                  </Link>
                )}
              </motion.div>
            );
          })}
        </div>
      </div>
    </PageTransition>
  );
}
