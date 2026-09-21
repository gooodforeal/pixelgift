import { useEffect, useId, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { Link, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Gift,
  Headset,
  LogIn,
  Menu,
  Shield,
  UserRound,
  X,
} from "lucide-react";

import { useAuth } from "../hooks/useAuth";
import { api } from "../lib/api";
import { UiThemeToggle } from "./UiThemeToggle";

function RailLogo({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <Link
      to="/"
      className="app-rail__logo"
      aria-label="Pixelgift — на главную"
      title="Pixelgift"
      onClick={onNavigate}
    >
      <span className="app-rail__logo-mark" aria-hidden>
        🎁
      </span>
      <span className="app-rail__brand">
        Pixel<span className="text-gradient">gift</span>
      </span>
    </Link>
  );
}

function RailLink({
  to,
  label,
  active,
  withLabel = false,
  onNavigate,
  children,
}: {
  to: string;
  label: string;
  active: boolean;
  withLabel?: boolean;
  onNavigate?: () => void;
  children: ReactNode;
}) {
  return (
    <Link
      to={to}
      className={`app-rail__link ${withLabel ? "has-label" : ""} ${
        active ? "is-active" : ""
      }`}
      aria-label={label}
      title={label}
      aria-current={active ? "page" : undefined}
      onClick={onNavigate}
    >
      <span className="app-rail__hit">
        <span className="app-rail__blob" aria-hidden />
        <span className="app-rail__icon">{children}</span>
      </span>
      {withLabel ? <span className="app-rail__caption">{label}</span> : null}
    </Link>
  );
}

function MenuLink({
  to,
  label,
  active,
  onNavigate,
  children,
}: {
  to: string;
  label: string;
  active: boolean;
  onNavigate: () => void;
  children: ReactNode;
}) {
  return (
    <Link
      to={to}
      className={`app-rail-menu__link ${active ? "is-active" : ""}`}
      aria-current={active ? "page" : undefined}
      onClick={onNavigate}
    >
      <span className="app-rail-menu__icon">{children}</span>
      <span>{label}</span>
    </Link>
  );
}

export function Header() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const path = location.pathname;
  const [menuOpen, setMenuOpen] = useState(false);
  const menuId = useId();
  const meQuery = useQuery({
    queryKey: ["me"],
    queryFn: api.me,
    enabled: isAuthenticated,
  });
  const isAdmin = Boolean(meQuery.data?.is_admin);

  const isBoxes = path === "/app" || path.startsWith("/app/boxes");
  const isProfile = path.startsWith("/app/profile");
  const isAdminArea = path.startsWith("/admin");
  const isSupport = path.startsWith("/support");
  const isLogin = path.startsWith("/login");

  const closeMenu = () => setMenuOpen(false);

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!menuOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    document.addEventListener("keydown", onKeyDown);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = prev;
    };
  }, [menuOpen]);

  return createPortal(
    <>
      <header className="app-rail" aria-label="Основная навигация">
        <div className="app-rail__inner">
          <RailLogo />

          <nav className="app-rail__nav" aria-label="Разделы">
            {isAuthenticated ? (
              <>
                <RailLink to="/app" label="Боксы" active={isBoxes} withLabel>
                  <Gift className="size-5" strokeWidth={2} />
                </RailLink>
                {isAdmin ? (
                  <RailLink
                    to="/admin"
                    label="Панель"
                    active={isAdminArea}
                    withLabel
                  >
                    <Shield className="size-5" strokeWidth={2} />
                  </RailLink>
                ) : null}
              </>
            ) : (
              <RailLink to="/login" label="Войти" active={isLogin} withLabel>
                <LogIn className="size-5" strokeWidth={2} />
              </RailLink>
            )}
            <RailLink to="/support" label="Поддержка" active={isSupport} withLabel>
              <Headset className="size-5" strokeWidth={2} />
            </RailLink>
          </nav>

          <div className="app-rail__footer">
            {isAuthenticated ? (
              <RailLink to="/app/profile" label="Профиль" active={isProfile}>
                <UserRound className="size-5" strokeWidth={2} />
              </RailLink>
            ) : null}
            <UiThemeToggle className="app-rail__theme" />
            <button
              type="button"
              className="app-rail__burger"
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
          </div>
        </div>
      </header>

      {menuOpen ? (
        <div
          id={menuId}
          className="app-rail-menu"
          role="dialog"
          aria-modal="true"
          aria-label="Меню"
        >
          <div className="app-rail-menu__bar">
            <RailLogo onNavigate={closeMenu} />
            <div className="app-rail-menu__bar-actions">
              <UiThemeToggle className="app-rail__theme" />
              <button
                type="button"
                className="app-rail__burger"
                aria-label="Закрыть меню"
                onClick={closeMenu}
              >
                <X className="size-5" strokeWidth={2.25} />
              </button>
            </div>
          </div>

          <nav className="app-rail-menu__nav" aria-label="Мобильная навигация">
            {isAuthenticated ? (
              <>
                <MenuLink
                  to="/app"
                  label="Боксы"
                  active={isBoxes}
                  onNavigate={closeMenu}
                >
                  <Gift className="size-5" strokeWidth={2} />
                </MenuLink>
                {isAdmin ? (
                  <MenuLink
                    to="/admin"
                    label="Панель"
                    active={isAdminArea}
                    onNavigate={closeMenu}
                  >
                    <Shield className="size-5" strokeWidth={2} />
                  </MenuLink>
                ) : null}
                <MenuLink
                  to="/app/profile"
                  label="Профиль"
                  active={isProfile}
                  onNavigate={closeMenu}
                >
                  <UserRound className="size-5" strokeWidth={2} />
                </MenuLink>
              </>
            ) : (
              <MenuLink
                to="/login"
                label="Войти"
                active={isLogin}
                onNavigate={closeMenu}
              >
                <LogIn className="size-5" strokeWidth={2} />
              </MenuLink>
            )}
            <MenuLink
              to="/support"
              label="Поддержка"
              active={isSupport}
              onNavigate={closeMenu}
            >
              <Headset className="size-5" strokeWidth={2} />
            </MenuLink>
          </nav>
        </div>
      ) : null}
    </>,
    document.body,
  );
}
