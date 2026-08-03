import { Link } from "react-router-dom";
import { Gift, Heart } from "lucide-react";

import { useAuth } from "../hooks/useAuth";
import { Logo } from "./Logo";
import { TelegramIcon } from "./TelegramIcon";

const year = new Date().getFullYear();

export function SiteFooter() {
  const { isAuthenticated } = useAuth();

  const links = isAuthenticated
    ? [
        { to: "/#how", label: "Как это работает" },
        { to: "/app", label: "Мои боксы" },
        { to: "/app/profile", label: "Профиль" },
        { to: "/app/boxes/new", label: "Новый бокс" },
      ]
    : [
        { to: "/#how", label: "Как это работает" },
        { to: "/login", label: "Создать бокс" },
        { to: "/login", label: "Войти", icon: true },
      ];

  return (
    <footer className="site-footer theme-site-footer mt-auto">
      <div className="site-footer__glow" aria-hidden />

      <div className="mx-auto w-full max-w-6xl px-3 sm:px-6">
        <div className="site-footer__panel">
          <div className="flex flex-col gap-8 md:flex-row md:items-end md:justify-between">
            <div className="max-w-md">
              <Logo />
              <p className="mt-4 text-sm leading-relaxed text-slate-400">
                Виртуальные подарочные боксы с таймером: фото, видео и голосовые
                откроются ровно в нужную секунду.
              </p>
              <p className="mt-3 inline-flex items-center gap-1.5 text-xs text-slate-500">
                <Gift className="size-3.5 text-glow-violet" />
                Собрали · спрятали · подарили
              </p>
            </div>

            <nav
              aria-label="Навигация в подвале"
              className="flex flex-wrap gap-x-5 gap-y-2 md:justify-end"
            >
              {links.map(({ to, label, icon }) => (
                <Link key={`${to}-${label}`} to={to} className="site-footer__link">
                  {icon ? <TelegramIcon className="size-3.5" /> : null}
                  {label}
                </Link>
              ))}
            </nav>
          </div>

          <div className="site-footer__meta">
            <span>© {year} Pixelgift</span>
            <span className="inline-flex items-center gap-1.5">
              Сделано с
              <Heart className="size-3 fill-glow-pink text-glow-pink" />
              для сюрпризов
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
