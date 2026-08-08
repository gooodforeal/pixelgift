import { Star } from "lucide-react";
import { useState } from "react";

interface DesignRatingStarsProps {
  average: number;
  count: number;
  myRating: number | null;
  interactive?: boolean;
  disabled?: boolean;
  pending?: boolean;
  onRate?: (stars: number) => void;
  className?: string;
}

export function DesignRatingStars({
  average,
  count,
  myRating,
  interactive = false,
  disabled = false,
  pending = false,
  onRate,
  className = "",
}: DesignRatingStarsProps) {
  const [hover, setHover] = useState<number | null>(null);
  const canRate = interactive && !disabled && myRating == null && !pending;
  const displayValue = hover ?? myRating ?? Math.round(average);

  return (
    <div
      className={`flex flex-wrap items-center gap-2 ${className}`}
      onMouseLeave={() => setHover(null)}
    >
      <div
        className="flex items-center gap-0.5"
        role={canRate ? "radiogroup" : "img"}
        aria-label={
          myRating != null
            ? `Ваша оценка: ${myRating} из 5`
            : count > 0
              ? `Средняя оценка ${average.toFixed(1)} из 5, ${count} оценок`
              : "Пока нет оценок"
        }
      >
        {[1, 2, 3, 4, 5].map((stars) => {
          const filled = displayValue >= stars;
          return (
            <button
              key={stars}
              type="button"
              disabled={!canRate}
              role={canRate ? "radio" : undefined}
              aria-checked={canRate ? myRating === stars : undefined}
              aria-label={`${stars} ${stars === 1 ? "звезда" : stars < 5 ? "звезды" : "звёзд"}`}
              className={`grid size-7 place-items-center rounded-md transition ${
                canRate
                  ? "cursor-pointer hover:bg-white/10"
                  : "cursor-default"
              } ${pending ? "opacity-60" : ""}`}
              onMouseEnter={() => {
                if (canRate) setHover(stars);
              }}
              onClick={(event) => {
                event.preventDefault();
                event.stopPropagation();
                if (!canRate || !onRate) return;
                onRate(stars);
              }}
            >
              <Star
                className={`size-4 ${
                  filled
                    ? "fill-amber-300 text-amber-300"
                    : "fill-transparent text-slate-500"
                }`}
                strokeWidth={1.75}
              />
            </button>
          );
        })}
      </div>
      <span className="text-[11px] tabular-nums text-slate-400">
        {count > 0 ? (
          <>
            {average.toFixed(1)}
            <span className="text-slate-500"> · {count}</span>
          </>
        ) : canRate ? (
          "Оцените"
        ) : (
          "Нет оценок"
        )}
        {myRating != null && (
          <span className="ml-1 text-slate-500">(ваша: {myRating})</span>
        )}
      </span>
    </div>
  );
}
