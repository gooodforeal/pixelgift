import { useEffect, useRef, useState, type ReactNode } from "react";
import { Ellipsis } from "lucide-react";

export type CardActionItem = {
  key: string;
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  disabled?: boolean;
  danger?: boolean;
};

interface CardActionsMenuProps {
  label?: string;
  items: CardActionItem[];
}

export function CardActionsMenu({
  label = "Действия",
  items,
}: CardActionsMenuProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node | null;
      if (!target || rootRef.current?.contains(target)) return;
      setOpen(false);
    };

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    window.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("pointerdown", onPointerDown);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  if (!items.length) return null;

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        className="btn-ghost size-8 px-0 py-0"
        aria-label={label}
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={() => setOpen((value) => !value)}
      >
        <Ellipsis className="size-4" />
      </button>

      {open ? (
        <div
          role="menu"
          className="box-card-menu absolute right-0 bottom-full z-20 mb-2 min-w-[11.5rem] overflow-hidden rounded-2xl border border-white/12 bg-ink-950/95 p-1 shadow-2xl shadow-black/40 backdrop-blur-xl"
        >
          {items.map((item) => (
            <button
              key={item.key}
              type="button"
              role="menuitem"
              className={`box-card-menu__item ${
                item.danger ? "box-card-menu__item--danger" : ""
              }`}
              disabled={item.disabled}
              onClick={() => {
                item.onClick();
                setOpen(false);
              }}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
