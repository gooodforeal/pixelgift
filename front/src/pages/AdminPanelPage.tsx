import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Palette, Shield } from "lucide-react";

import { PageTransition } from "../components/PageTransition";

const SECTIONS = [
  {
    to: "/admin/designs",
    title: "Дизайны",
    description: "Темы коробок, палитры, обложки и активность.",
    icon: Palette,
  },
] as const;

export function AdminPanelPage() {
  return (
    <PageTransition>
      <div className="pt-10 pb-6 sm:pt-14">
        <p className="chip w-fit">
          <Shield className="size-3.5" />
          Админ
        </p>
        <h1 className="mt-3 font-sans text-2xl font-semibold tracking-tight sm:text-3xl">
          Панель
        </h1>
        <p className="mt-2 max-w-xl text-sm text-slate-400">
          Управление продуктом. Сюда будут добавляться новые разделы.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {SECTIONS.map((section, index) => (
            <motion.div
              key={section.to}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.04 }}
            >
              <Link
                to={section.to}
                className="glass group flex h-full flex-col gap-3 p-5 transition hover:border-white/20 sm:p-6"
              >
                <span className="grid size-11 place-items-center rounded-2xl border border-white/10 bg-white/[0.05] text-glow-cyan transition group-hover:border-glow-violet/40 group-hover:text-glow-violet">
                  <section.icon className="size-5" />
                </span>
                <div>
                  <h2 className="font-sans text-base font-semibold text-slate-100">
                    {section.title}
                  </h2>
                  <p className="mt-1.5 text-sm leading-relaxed text-slate-400">
                    {section.description}
                  </p>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </PageTransition>
  );
}
