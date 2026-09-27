import { useEffect, useId, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { Link, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Gift,
  Menu,
  Package,
  Shield,
  ShoppingCart,
  UserRound,
  X,
} from "lucide-react";

import { useAuth } from "../hooks/useAuth";
import { api } from "../lib/api";
import { pluralize } from "../lib/format";
import { CartDropdown } from "./CartDropdown";
import { LogoMark } from "./Logo";
import { UiThemeToggle } from "./UiThemeToggle";

function OpenedThisMonthStat({ className = "" }: { className?: string }) {
  const statsQuery = useQuery({
    queryKey: ["boxes", "opens"],
    queryFn: api.openedThisMonth,
    staleTime: 60_000,
    refetchOnWindowFocus: false,
  });

  if (!statsQuery.data) return null;

  const count = statsQuery.data.count;
  const giftsWord = pluralize(count, ["подарок", "подарка", "подарков"]);
  const label = `${count} ${giftsWord} открыто в этом месяце`;

  return (
    <p className={`app-rail__stat ${className}`} title={label}>
      <span className="app-rail__stat-line">
        <span className="app-rail__stat-count">{count}</span>
        <span className="app-rail__stat-word"> {giftsWord}</span>
      </span>
      <span className="app-rail__stat-sub">открыто в этом месяце</span>
    </p>
  );
}

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
        <LogoMark className="app-rail__logo-gift" />
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
  const [cartOpen, setCartOpen] = useState(false);
  const menuId = useId();
  const meQuery = useQuery({
    queryKey: ["me"],
    queryFn: api.me,
    enabled: isAuthenticated,
  });
  const cartQuery = useQuery({
    queryKey: ["cart"],
    queryFn: api.cart,
    enabled: isAuthenticated,
    staleTime: 30_000,
  });
  const isAdmin = Boolean(meQuery.data?.is_admin);
  const cartCount =
    cartQuery.data?.items.reduce((sum, item) => sum + item.quantity, 0) ?? 0;

  const isBoxes = path === "/app" || path.startsWith("/app/boxes");
  const isProfile = path.startsWith("/app/profile");
  const isProducts = path.startsWith("/products");
  const isAdminArea = path.startsWith("/app/panel");
  const isLogin = path.startsWith("/login");

  const closeMenu = () => setMenuOpen(false);

  useEffect(() => {
    setMenuOpen(false);
    setCartOpen(false);
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
          <div className="app-rail__lead">
            <RailLogo />
            <OpenedThisMonthStat className="app-rail__stat--desktop" />
          </div>

          <nav className="app-rail__nav" aria-label="Разделы">
            {isAuthenticated ? (
              <>
                <RailLink to="/app" label="Боксы" active={isBoxes} withLabel>
                  <Gift className="size-5" strokeWidth={2} />
                </RailLink>
                <RailLink
                  to="/products"
                  label="Товары"
                  active={isProducts}
                  withLabel
                >
                  <Package className="size-5" strokeWidth={2} />
                </RailLink>
                {isAdmin ? (
                  <RailLink
                    to="/app/panel"
                    label="Панель"
                    active={isAdminArea}
                    withLabel
                  >
                    <Shield className="size-5" strokeWidth={2} />
                  </RailLink>
                ) : null}
              </>
            ) : (
              <RailLink
                to="/products"
                label="Товары"
                active={isProducts}
                withLabel
              >
                <Package className="size-5" strokeWidth={2} />
              </RailLink>
            )}
          </nav>

          <div className="app-rail__footer">
            {isAuthenticated ? (
              <>
                <CartDropdown
                  open={cartOpen}
                  onOpenChange={setCartOpen}
                  cartCount={cartCount}
                />
                <RailLink to="/app/profile" label="Профиль" active={isProfile}>
                  <UserRound className="size-5" strokeWidth={2} />
                </RailLink>
              </>
            ) : (
              <Link
                to="/login"
                className={`btn-primary app-rail__login${
                  isLogin ? " is-active" : ""
                }`}
                aria-current={isLogin ? "page" : undefined}
              >
                Войти
              </Link>
            )}
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
            <OpenedThisMonthStat className="app-rail__stat--menu" />
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
                <MenuLink
                  to="/products"
                  label="Товары"
                  active={isProducts}
                  onNavigate={closeMenu}
                >
                  <Package className="size-5" strokeWidth={2} />
                </MenuLink>
                <button
                  type="button"
                  className="app-rail-menu__link"
                  onClick={() => {
                    closeMenu();
                    setCartOpen(true);
                  }}
                >
                  <span className="app-rail-menu__icon relative inline-flex">
                    <ShoppingCart className="size-5" strokeWidth={2} />
                    {cartCount > 0 ? (
                      <span className="app-rail__badge" aria-hidden>
                        {cartCount > 99 ? "99+" : cartCount}
                      </span>
                    ) : null}
                  </span>
                  <span>
                    {cartCount > 0 ? `Корзина · ${cartCount}` : "Корзина"}
                  </span>
                </button>
                {isAdmin ? (
                  <MenuLink
                    to="/app/panel"
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
                to="/products"
                label="Товары"
                active={isProducts}
                onNavigate={closeMenu}
              >
                <Package className="size-5" strokeWidth={2} />
              </MenuLink>
            )}
          </nav>
        </div>
      ) : null}
    </>,
    document.body,
  );
}
