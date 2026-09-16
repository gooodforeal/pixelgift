import { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Link, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { LayoutGrid, Menu, Shield, UserRound, X } from "lucide-react";

import { useAuth } from "../hooks/useAuth";
import { api } from "../lib/api";
import { Logo } from "./Logo";
import { TelegramIcon } from "./TelegramIcon";
import { UiThemeToggle } from "./UiThemeToggle";

export function Header() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuId = useId();
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const meQuery = useQuery({
    queryKey: ["me"],
    queryFn: api.me,
    enabled: isAuthenticated,
  });
  const isAdmin = Boolean(meQuery.data?.is_admin);

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const media = window.matchMedia("(min-width: 768px)");
    const onChange = () => {
      if (media.matches) setMenuOpen(false);
    };
    onChange();
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  useEffect(() => {
    if (!menuOpen) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };

    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node;
      if (
        menuRef.current?.contains(target) ||
        buttonRef.current?.contains(target)
      ) {
        return;
      }
      setMenuOpen(false);
    };

    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("pointerdown", onPointerDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("pointerdown", onPointerDown);
    };
  }, [menuOpen]);

  return createPortal(
    <header className="app-header">
      <div className="relative mx-auto flex h-14 max-w-6xl items-center justify-between gap-2 px-3 sm:h-16 sm:gap-3 sm:px-6">
        <Logo to="/" />

        <div className="flex shrink-0 items-center gap-1.5 sm:gap-2.5">
          <nav className="header-desktop-nav">
            {isAuthenticated ? (
              <>
                <Link
                  to="/app"
                  className="header-nav-btn"
                  aria-label="Мои боксы"
                  title="Мои боксы"
                >
                  <LayoutGrid className="size-4 shrink-0" />
                  <span>Мои боксы</span>
                </Link>
                {isAdmin ? (
                  <Link
                    to="/admin"
                    className="header-nav-btn"
                    aria-label="Панель"
                    title="Панель"
                  >
                    <Shield className="size-4 shrink-0" />
                    <span>Панель</span>
                  </Link>
                ) : null}
                <Link
                  to="/app/profile"
                  className="header-nav-btn"
                  aria-label="Профиль"
                  title="Профиль"
                >
                  <UserRound className="size-4 shrink-0" />
                  <span>Профиль</span>
                </Link>
              </>
            ) : (
              <Link to="/login" className="btn-primary px-5 py-2.5 text-sm">
                <TelegramIcon className="size-4 shrink-0" />
                Войти через Telegram
              </Link>
            )}
          </nav>

          <button
            ref={buttonRef}
            type="button"
            className="header-menu-btn"
            aria-label={menuOpen ? "Закрыть меню" : "Открыть меню"}
            aria-expanded={menuOpen}
            aria-controls={menuId}
            onClick={() => setMenuOpen((open) => !open)}
          >
            {menuOpen ? (
              <X className="size-5" strokeWidth={2.25} />
            ) : (
              <Menu className="size-5" strokeWidth={2.25} />
            )}
          </button>

          <UiThemeToggle />
        </div>

        {menuOpen ? (
          <div
            ref={menuRef}
            id={menuId}
            className="header-menu absolute inset-x-3 top-[calc(100%+0.5rem)]"
            role="menu"
          >
            {isAuthenticated ? (
              <>
                <Link to="/app" className="header-menu__link" role="menuitem">
                  <LayoutGrid className="size-4 shrink-0" />
                  Мои боксы
                </Link>
                {isAdmin ? (
                  <Link
                    to="/admin"
                    className="header-menu__link"
                    role="menuitem"
                  >
                    <Shield className="size-4 shrink-0" />
                    Панель
                  </Link>
                ) : null}
                <Link
                  to="/app/profile"
                  className="header-menu__link"
                  role="menuitem"
                >
                  <UserRound className="size-4 shrink-0" />
                  Профиль
                </Link>
              </>
            ) : (
              <Link to="/login" className="header-menu__link" role="menuitem">
                <TelegramIcon className="size-4 shrink-0" />
                Войти через Telegram
              </Link>
            )}
          </div>
        ) : null}
      </div>
    </header>,
    document.body,
  );
}
