import { Moon, Sun } from "lucide-react";

import { useUiTheme } from "../hooks/useUiTheme";

type UiThemeToggleProps = {
  className?: string;
};

export function UiThemeToggle({ className = "" }: UiThemeToggleProps) {
  const { theme, toggleTheme } = useUiTheme();
  const isDark = theme === "dark";

  return (
    <button
      type="button"
      className={`theme-toggle-btn ${className}`}
      onClick={toggleTheme}
      aria-label={isDark ? "Включить светлую тему" : "Включить тёмную тему"}
      title={isDark ? "Светлая тема" : "Тёмная тема"}
    >
      {isDark ? (
        <Sun className="size-[1.125rem]" strokeWidth={2.25} />
      ) : (
        <Moon className="size-[1.125rem]" strokeWidth={2.25} />
      )}
    </button>
  );
}
