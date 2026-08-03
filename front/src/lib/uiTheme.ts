export type UiTheme = "dark" | "light";

export const UI_THEME_STORAGE_KEY = "pixelgift.ui-theme";

export function resolveInitialUiTheme(): UiTheme {
  if (typeof window === "undefined") return "dark";

  const stored = window.localStorage.getItem(UI_THEME_STORAGE_KEY);
  if (stored === "light" || stored === "dark") return stored;

  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

export function applyUiTheme(theme: UiTheme) {
  document.documentElement.dataset.theme = theme;
  document.documentElement.style.colorScheme = theme;
}

export function persistUiTheme(theme: UiTheme) {
  window.localStorage.setItem(UI_THEME_STORAGE_KEY, theme);
}
