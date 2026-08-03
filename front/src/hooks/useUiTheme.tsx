import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  applyUiTheme,
  persistUiTheme,
  resolveInitialUiTheme,
  type UiTheme,
} from "../lib/uiTheme";

type UiThemeContextValue = {
  theme: UiTheme;
  setTheme: (theme: UiTheme) => void;
  toggleTheme: () => void;
};

const UiThemeContext = createContext<UiThemeContextValue | null>(null);

export function UiThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<UiTheme>(() => resolveInitialUiTheme());

  useEffect(() => {
    applyUiTheme(theme);
    persistUiTheme(theme);
  }, [theme]);

  const setTheme = useCallback((next: UiTheme) => {
    setThemeState(next);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((current) => (current === "dark" ? "light" : "dark"));
  }, []);

  const value = useMemo(
    () => ({ theme, setTheme, toggleTheme }),
    [theme, setTheme, toggleTheme],
  );

  return <UiThemeContext.Provider value={value}>{children}</UiThemeContext.Provider>;
}

export function useUiTheme() {
  const ctx = useContext(UiThemeContext);
  if (!ctx) {
    throw new Error("useUiTheme must be used within UiThemeProvider");
  }
  return ctx;
}
