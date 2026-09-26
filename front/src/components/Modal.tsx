import { useEffect, useId, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";

interface ModalProps {
  open: boolean;
  title: string;
  description?: string;
  onClose: () => void;
  children: ReactNode;
  footer?: ReactNode;
  size?: "md" | "lg";
}

export function Modal({
  open,
  title,
  description,
  onClose,
  children,
  footer,
  size = "md",
}: ModalProps) {
  const titleId = useId();
  const descriptionId = useId();

  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open, onClose]);

  if (typeof document === "undefined") return null;

  const widthClass =
    size === "lg"
      ? "w-[min(36rem,calc(100vw-2rem))]"
      : "w-[min(28rem,calc(100vw-2rem))]";

  return createPortal(
    <AnimatePresence>
      {open ? (
        <>
          <motion.button
            key="admin-modal-backdrop"
            type="button"
            aria-label="Закрыть"
            className="fixed inset-0 z-[120] border-0 bg-ink-950/70 p-0 backdrop-blur-[2px]"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            onClick={onClose}
          />
          <div className="pointer-events-none fixed inset-0 z-[121] flex items-center justify-center p-4">
            <motion.div
              key="admin-modal-dialog"
              role="dialog"
              aria-modal="true"
              aria-labelledby={titleId}
              aria-describedby={description ? descriptionId : undefined}
              initial={{ opacity: 0, scale: 0.96, y: 12 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.98, y: 8 }}
              transition={{ duration: 0.2 }}
              className={`glass pointer-events-auto flex max-h-[min(88dvh,40rem)] ${widthClass} flex-col overflow-hidden !rounded-2xl shadow-2xl`}
            >
              <header className="flex shrink-0 items-start justify-between gap-3 border-b border-white/10 px-5 py-4">
                <div className="min-w-0">
                  <h2
                    id={titleId}
                    className="font-sans text-lg font-semibold text-slate-100"
                  >
                    {title}
                  </h2>
                  {description ? (
                    <p
                      id={descriptionId}
                      className="mt-1 text-sm text-slate-400"
                    >
                      {description}
                    </p>
                  ) : null}
                </div>
                <button
                  type="button"
                  className="btn-ghost size-9 shrink-0 px-0!"
                  aria-label="Закрыть"
                  onClick={onClose}
                >
                  <X className="size-4" />
                </button>
              </header>
              <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
                {children}
              </div>
              {footer ? (
                <footer className="flex shrink-0 flex-wrap items-center justify-end gap-2 border-t border-white/10 px-5 py-4">
                  {footer}
                </footer>
              ) : null}
            </motion.div>
          </div>
        </>
      ) : null}
    </AnimatePresence>,
    document.body,
  );
}
