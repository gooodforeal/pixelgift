import { useCallback, useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, Eye } from "lucide-react";
import { motion } from "framer-motion";

import { DesignCover } from "./DesignCover";
import { DesignRatingStars } from "./DesignRatingStars";
import {
  DesignPreviewPopover,
  type DesignPreviewAnchor,
} from "./DesignPreviewPopover";
import { ApiError, api } from "../lib/api";
import { useAuth } from "../hooks/useAuth";
import { gradientCss, resolveTheme } from "../lib/theme";
import type { BoxDesign, DesignRating } from "../lib/types";

interface DesignPickerProps {
  designs: BoxDesign[];
  selectedId: string | null;
  onSelect: (designId: string) => void;
  disabled?: boolean;
}

function patchDesignRating(
  designs: BoxDesign[] | undefined,
  rating: DesignRating,
): BoxDesign[] | undefined {
  if (!designs) return designs;
  return designs.map((design) =>
    design.id === rating.design_id
      ? {
          ...design,
          rating_avg: rating.rating_avg,
          rating_count: rating.rating_count,
          my_rating: rating.stars,
        }
      : design,
  );
}

export function DesignPicker({
  designs,
  selectedId,
  onSelect,
  disabled = false,
}: DesignPickerProps) {
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const [previewAnchor, setPreviewAnchor] = useState<DesignPreviewAnchor | null>(
    null,
  );
  const [ratingError, setRatingError] = useState<string | null>(null);

  const rateMutation = useMutation({
    mutationFn: ({ designId, stars }: { designId: string; stars: number }) =>
      api.rateDesign(designId, stars),
    onSuccess: (rating) => {
      setRatingError(null);
      queryClient.setQueryData<BoxDesign[]>(["designs"], (current) =>
        patchDesignRating(current, rating),
      );
    },
    onError: (error) => {
      if (error instanceof ApiError && error.status === 409) {
        setRatingError("Вы уже оценили этот дизайн");
        return;
      }
      setRatingError("Не удалось сохранить оценку");
    },
  });

  const closePreview = useCallback(() => {
    setPreviewAnchor(null);
  }, []);

  const togglePreview = useCallback((design: BoxDesign) => {
    setPreviewAnchor((current) =>
      current?.design.id === design.id ? null : { design },
    );
  }, []);

  useEffect(() => {
    if (!previewAnchor) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") closePreview();
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [closePreview, previewAnchor]);

  return (
    <>
      <div
        className={`grid grid-cols-1 gap-3 min-[420px]:grid-cols-2 sm:gap-4 lg:grid-cols-3 ${disabled ? "opacity-80" : ""}`}
      >
        {designs.map((design) => {
          const theme = resolveTheme(design);
          const selected = design.id === selectedId;
          const previewOpen = previewAnchor?.design.id === design.id;
          const ratingPending =
            rateMutation.isPending &&
            rateMutation.variables?.designId === design.id;

          return (
            <div key={design.id} className="relative min-w-0">
              <motion.button
                type="button"
                disabled={disabled}
                onClick={() => onSelect(design.id)}
                whileHover={disabled ? undefined : { y: -4 }}
                whileTap={disabled ? undefined : { scale: 0.985 }}
                className={`design-picker-card group relative isolate flex h-full w-full max-w-full overflow-hidden rounded-3xl border p-px text-left transition ${
                  selected ? "border-transparent" : "border-white/10 hover:border-white/25"
                } ${disabled ? "cursor-default hover:border-white/10" : ""}`}
                style={
                  selected ? { background: gradientCss(theme.gradient, 120) } : undefined
                }
              >
                <div className="design-theme-card relative flex h-full min-w-0 w-full flex-col overflow-hidden rounded-[1.35rem] bg-ink-900">
                  <DesignCover
                    code={design.code}
                    previewImageUrl={design.preview_image_url}
                    themeConfig={design.theme_config}
                    heightClassName="h-28 w-full shrink-0 sm:h-36"
                  >
                    {selected && (
                      <span className="absolute top-3 right-3 z-10 grid size-7 place-items-center rounded-full bg-white/90 text-ink-950">
                        <Check className="size-4" strokeWidth={3} />
                      </span>
                    )}
                  </DesignCover>
                  <div className="design-theme-card__body flex flex-1 flex-col gap-1 p-3.5 sm:p-4">
                    <div className="design-theme-card__title font-sans text-sm font-semibold text-slate-100">
                      {design.name}
                    </div>
                    {design.description && (
                      <p className="design-theme-card__desc text-xs text-slate-400">
                        {design.description}
                      </p>
                    )}
                    <div
                      className="mt-2"
                      onClick={(event) => {
                        event.preventDefault();
                        event.stopPropagation();
                      }}
                    >
                      <DesignRatingStars
                        average={design.rating_avg ?? 0}
                        count={design.rating_count ?? 0}
                        myRating={design.my_rating ?? null}
                        interactive={isAuthenticated && !disabled}
                        pending={ratingPending}
                        onRate={(stars) =>
                          rateMutation.mutate({ designId: design.id, stars })
                        }
                      />
                    </div>
                  </div>
                </div>
              </motion.button>

              <button
                type="button"
                data-design-preview-toggle
                className={`absolute top-3 z-20 grid size-8 place-items-center rounded-full border shadow-md backdrop-blur-md transition ${
                  selected ? "left-3" : "right-3"
                } ${
                  previewOpen
                    ? "border-white/50 bg-white text-ink-950"
                    : "border-white/25 bg-black/45 text-white hover:bg-black/60"
                }`}
                aria-label={`Превью темы «${design.name}»`}
                aria-pressed={previewOpen}
                title="Пример открытия"
                onClick={(event) => {
                  event.preventDefault();
                  event.stopPropagation();
                  togglePreview(design);
                }}
              >
                <Eye className="size-3.5" strokeWidth={2.25} />
              </button>
            </div>
          );
        })}
      </div>

      {ratingError && (
        <p className="mt-3 text-sm text-rose-300" role="alert">
          {ratingError}
        </p>
      )}

      <DesignPreviewPopover
        anchor={previewAnchor}
        onRequestClose={closePreview}
      />
    </>
  );
}
