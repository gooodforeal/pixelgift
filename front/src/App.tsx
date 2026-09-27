import { useEffect, useState, type ReactNode } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

import { Header } from "./components/Header";
import { SiteFooter } from "./components/SiteFooter";
import { Spinner } from "./components/Spinner";
import { useAuth } from "./hooks/useAuth";
import { api, bootstrapAuth } from "./lib/api";
import { AdminDesignEditorPage } from "./pages/AdminDesignEditorPage";
import { AdminDesignsPage } from "./pages/AdminDesignsPage";
import { AdminPanelPage } from "./pages/AdminPanelPage";
import { AdminProductsPage } from "./pages/AdminProductsPage";
import { AdminPromoCodesPage } from "./pages/AdminPromoCodesPage";
import { AdminSupportPage } from "./pages/AdminSupportPage";
import { BoxEditorPage } from "./pages/BoxEditorPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ProductsPage } from "./pages/ProductsPage";
import { ProductPage } from "./pages/ProductPage";
import { ProfilePage } from "./pages/ProfilePage";
import { PublicBoxPage } from "./pages/PublicBoxPage";
import { SupportPage } from "./pages/SupportPage";

function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return children;
}

function RequireAdmin({ children }: { children: ReactNode }) {
  const meQuery = useQuery({ queryKey: ["me"], queryFn: api.me });

  if (meQuery.isPending) {
    return <Spinner label="Проверяем доступ…" className="py-32" />;
  }

  if (meQuery.isError || !meQuery.data?.is_admin) {
    return <Navigate to="/app" replace />;
  }

  return children;
}

function AppShell({
  children,
  fullBleed = false,
}: {
  children: ReactNode;
  fullBleed?: boolean;
}) {
  return (
    <div className="relative flex min-h-dvh flex-col">
      <main
        className={
          fullBleed
            ? "theme-canvas w-full flex-1 pt-14 sm:pt-16"
            : "theme-canvas mx-auto w-full max-w-6xl flex-1 px-3 pt-14 pb-10 sm:px-6 sm:pt-16 sm:pb-12"
        }
      >
        {children}
      </main>
      <SiteFooter />
    </div>
  );
}

export function App() {
  const location = useLocation();
  const [authReady, setAuthReady] = useState(false);
  const showHeader = !location.pathname.startsWith("/b/");

  useEffect(() => {
    let cancelled = false;
    void bootstrapAuth().finally(() => {
      if (!cancelled) setAuthReady(true);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!authReady) {
    return <Spinner label="Загружаем…" className="py-32" />;
  }

  return (
    <>
      {showHeader ? <Header /> : null}
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/b/:slug" element={<PublicBoxPage />} />

          <Route
            path="/"
            element={
              <AppShell fullBleed>
                <LandingPage />
              </AppShell>
            }
          />
          <Route
            path="/login"
            element={
              <AppShell>
                <LoginPage />
              </AppShell>
            }
          />
          <Route
            path="/app"
            element={
              <RequireAuth>
                <AppShell>
                  <DashboardPage />
                </AppShell>
              </RequireAuth>
            }
          />
          <Route
            path="/app/profile"
            element={
              <RequireAuth>
                <AppShell>
                  <ProfilePage />
                </AppShell>
              </RequireAuth>
            }
          />
          <Route
            path="/products"
            element={
              <AppShell>
                <ProductsPage />
              </AppShell>
            }
          />
          <Route
            path="/products/:productId"
            element={
              <AppShell>
                <ProductPage />
              </AppShell>
            }
          />
          <Route
            path="/app/cart"
            element={<Navigate to="/products" replace />}
          />
          <Route
            path="/app/boxes/new"
            element={
              <RequireAuth>
                <AppShell>
                  <BoxEditorPage />
                </AppShell>
              </RequireAuth>
            }
          />
          <Route
            path="/app/boxes/:boxId"
            element={
              <RequireAuth>
                <AppShell>
                  <BoxEditorPage />
                </AppShell>
              </RequireAuth>
            }
          />
          <Route
            path="/support"
            element={
              <AppShell>
                <SupportPage />
              </AppShell>
            }
          />
          <Route
            path="/app/panel"
            element={
              <RequireAuth>
                <RequireAdmin>
                  <AppShell>
                    <AdminPanelPage />
                  </AppShell>
                </RequireAdmin>
              </RequireAuth>
            }
          />
          <Route
            path="/app/panel/products"
            element={
              <RequireAuth>
                <RequireAdmin>
                  <AppShell>
                    <AdminProductsPage />
                  </AppShell>
                </RequireAdmin>
              </RequireAuth>
            }
          />
          <Route
            path="/app/panel/promo-codes"
            element={
              <RequireAuth>
                <RequireAdmin>
                  <AppShell>
                    <AdminPromoCodesPage />
                  </AppShell>
                </RequireAdmin>
              </RequireAuth>
            }
          />
          <Route
            path="/app/panel/support"
            element={
              <RequireAuth>
                <RequireAdmin>
                  <AppShell>
                    <AdminSupportPage />
                  </AppShell>
                </RequireAdmin>
              </RequireAuth>
            }
          />
          <Route
            path="/app/panel/designs"
            element={
              <RequireAuth>
                <RequireAdmin>
                  <AppShell>
                    <AdminDesignsPage />
                  </AppShell>
                </RequireAdmin>
              </RequireAuth>
            }
          />
          <Route
            path="/app/panel/designs/new"
            element={
              <RequireAuth>
                <RequireAdmin>
                  <AppShell>
                    <AdminDesignEditorPage />
                  </AppShell>
                </RequireAdmin>
              </RequireAuth>
            }
          />
          <Route
            path="/app/panel/designs/:designId"
            element={
              <RequireAuth>
                <RequireAdmin>
                  <AppShell>
                    <AdminDesignEditorPage />
                  </AppShell>
                </RequireAdmin>
              </RequireAuth>
            }
          />
          <Route
            path="*"
            element={
              <AppShell>
                <NotFoundPage />
              </AppShell>
            }
          />
        </Routes>
      </AnimatePresence>
    </>
  );
}
