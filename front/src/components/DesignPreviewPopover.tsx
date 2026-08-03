import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";

import { DesignGiftPreview } from "./DesignGiftPreview";
import type { BoxDesign } from "../lib/types";

type Anchor = {
  design: BoxDesign;
};

interface DesignPreviewPopoverProps {
  anchor: Anchor | null;
  onRequestClose: () => void;
}

export function DesignPreviewPopover({
  anchor,
  onRequestClose,
}: DesignPreviewPopoverProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!anchor) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const onPointerDown = (event: PointerEvent) => {
      const target = event.target as Node | null;
      if (!target) return;
      if (dialogRef.current?.contains(target)) return;
      if (target instanceof Element && target.closest("[data-design-preview-toggle]")) {
        return;
      }
      onRequestClose();
    };

    window.addEventListener("pointerdown", onPointerDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("pointerdown", onPointerDown);
    };
  }, [anchor, onRequestClose]);

  if (typeof document === "undefined") return null;

  return createPortal(
    <AnimatePresence>
      {anchor && (
        <>
          <motion.button
            key="design-preview-backdrop"
            type="button"
            aria-label="Закрыть превью"
            className="design-preview-popover__backdrop fixed inset-0 z-[120] border-0 p-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            onClick={onRequestClose}
          />

          <motion.div
            key="design-preview-dialog"
            ref={dialogRef}
            role="dialog"
            aria-modal="true"
            aria-label={`Пример открытия: ${anchor.design.name}`}
            initial={{ opacity: 0, scale: 0.94, x: "-50%", y: "calc(-50% + 16px)" }}
            animate={{ opacity: 1, scale: 1, x: "-50%", y: "-50%" }}
            exit={{ opacity: 0, scale: 0.96, x: "-50%", y: "calc(-50% + 10px)" }}
            transition={{ duration: 0.2 }}
            className="design-preview-popover fixed top-1/2 left-1/2 z-[121] flex h-[min(42rem,88dvh)] w-[min(24rem,calc(100vw-2rem))] flex-col overflow-hidden rounded-[1.75rem] border shadow-2xl"
          >
            <div className="design-preview-popover__chrome relative shrink-0 border-b px-4 py-3 pr-12 text-center">
              <p className="text-[0.7rem] font-semibold tracking-wide uppercase opacity-80">
                Пример открытия
              </p>
              <p className="font-display truncate text-sm">{anchor.design.name}</p>
              <button
                type="button"
                className="design-preview-popover__close absolute top-2.5 right-2.5 grid size-8 place-items-center rounded-full transition"
                aria-label="Закрыть превью"
                onClick={onRequestClose}
              >
                <X className="size-4" strokeWidth={2.5} />
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-hidden">
              <DesignGiftPreview design={anchor.design} />
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>,
    document.body,
  );
}

export type { Anchor as DesignPreviewAnchor };
