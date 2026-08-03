import { useEffect, useId, useLayoutEffect, useRef, useState, type CSSProperties } from "react";
import { createPortal } from "react-dom";
import { Check, ChevronDown } from "lucide-react";

import { PARTICLE_OPTIONS, type ParticleKind } from "../lib/particles";

interface ParticleSelectProps {
  value: ParticleKind;
  onChange: (value: ParticleKind) => void;
}

export function ParticleSelect({ value, onChange }: ParticleSelectProps) {
  const [open, setOpen] = useState(false);
  const [menuStyle, setMenuStyle] = useState<CSSProperties>({});
  const rootRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLUListElement>(null);
  const listId = useId();
  const selected =
    PARTICLE_OPTIONS.find((option) => option.value === value) ?? PARTICLE_OPTIONS[3];

  useLayoutEffect(() => {
    if (!open || !buttonRef.current) return;

    const updatePosition = () => {
      const rect = buttonRef.current!.getBoundingClientRect();
      const menuHeight = Math.min(256, window.innerHeight - 24);
      const spaceBelow = window.innerHeight - rect.bottom - 12;
      const openUp = spaceBelow < 180 && rect.top > spaceBelow;
      setMenuStyle({
        position: "fixed",
        left: rect.left,
        width: rect.width,
        top: openUp ? undefined : rect.bottom + 8,
        bottom: openUp ? window.innerHeight - rect.top + 8 : undefined,
        maxHeight: openUp ? Math.min(menuHeight, rect.top - 12) : Math.min(menuHeight, spaceBelow),
        zIndex: 80,
      });
    };

    updatePosition();
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);
    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition, true);
    };
  }, [open]);

  useEffect(() => {
    if (!open) return;

    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node;
      if (rootRef.current?.contains(target) || menuRef.current?.contains(target)) {
        return;
      }
      setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  return (
    <div ref={rootRef} className="particle-select relative">
      <button
        ref={buttonRef}
        type="button"
        className="field flex w-full items-center gap-2.5 py-2.5 text-left"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listId}
        onClick={() => setOpen((current) => !current)}
      >
        <span className="particle-select__glyph" aria-hidden>
          {selected.glyph}
        </span>
        <span className="min-w-0 flex-1 truncate">{selected.label}</span>
        <ChevronDown
          className={`size-4 shrink-0 text-slate-400 transition ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open
        ? createPortal(
            <ul
              ref={menuRef}
              id={listId}
              role="listbox"
              className="particle-select__menu overflow-auto p-1.5"
              style={menuStyle}
            >
              {PARTICLE_OPTIONS.map((option) => {
                const active = option.value === value;
                return (
                  <li key={option.value} role="option" aria-selected={active}>
                    <button
                      type="button"
                      className={`particle-select__option ${active ? "is-active" : ""}`}
                      onClick={() => {
                        onChange(option.value);
                        setOpen(false);
                      }}
                    >
                      <span className="particle-select__glyph" aria-hidden>
                        {option.glyph}
                      </span>
                      <span className="min-w-0 flex-1 text-left">{option.label}</span>
                      {active ? (
                        <Check className="size-3.5 shrink-0 opacity-80" />
                      ) : null}
                    </button>
                  </li>
                );
              })}
            </ul>,
            document.body,
          )
        : null}
    </div>
  );
}
