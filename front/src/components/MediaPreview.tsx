import { useState } from "react";
import { Check, MapPin, X } from "lucide-react";

import { CirclePlayer } from "./CirclePlayer";
import type { BoxItemType } from "../lib/types";
import {
  formatGeopointCoords,
  geopointFromMetadata,
  osmMapUrl,
  type GeopointCoords,
} from "../lib/geopoint";
import { questionFromMetadata } from "../lib/question";
import { getToyOption, toyImageUrl } from "../lib/toys";

interface MediaPreviewProps {
  src: string;
  type: BoxItemType;
  className?: string;
  /** `cover` crops to fill; `contain` shows the whole media (default for gift reveal). */
  fit?: "cover" | "contain";
  /** Circle items play on tap when true; editor thumbs pass false. */
  interactive?: boolean;
  caption?: string | null;
  toyCode?: string | null;
  geopoint?: GeopointCoords | null;
  metadata?: Record<string, unknown> | null;
}

export function MediaPreview({
  src,
  type,
  className = "",
  fit = "contain",
  interactive = true,
  caption,
  toyCode,
  geopoint,
  metadata,
}: MediaPreviewProps) {
  const objectFit = fit === "cover" ? "object-cover" : "object-contain";

  if (type === "circle") {
    return (
      <CirclePlayer
        src={src}
        className={className}
        interactive={interactive}
      />
    );
  }

  if (type === "video") {
    return (
      <video
        src={src}
        controls
        playsInline
        preload="metadata"
        className={`h-full w-full bg-black/40 ${objectFit} ${className}`}
      />
    );
  }

  if (type === "voice") {
    return (
      <div
        className={`flex h-full min-h-[12rem] w-full flex-col items-center justify-center gap-5 bg-gradient-to-br from-ink-800/90 to-ink-700/80 p-6 sm:p-8 ${className}`}
      >
        <div className="flex size-16 items-center justify-center rounded-full bg-glow-violet/20 text-4xl shadow-lg shadow-glow-violet/20">
          🎙️
        </div>
        {caption ? (
          <p className="max-w-md text-center text-sm text-slate-300">{caption}</p>
        ) : (
          <p className="text-sm text-slate-400">Голосовое сообщение</p>
        )}
        <audio
          src={src}
          controls
          preload="metadata"
          className="w-full max-w-md"
          style={{ colorScheme: "dark" }}
        >
          Ваш браузер не поддерживает воспроизведение аудио.
        </audio>
      </div>
    );
  }

  if (type === "text") {
    return (
      <div
        className={`flex h-full min-h-[10rem] w-full items-center justify-center bg-gradient-to-br from-ink-800/80 to-ink-700/70 p-6 sm:p-8 ${className}`}
      >
        <p className="max-w-lg whitespace-pre-wrap text-center text-base leading-relaxed text-slate-100 sm:text-lg">
          {caption?.trim() || "Пустой текст"}
        </p>
      </div>
    );
  }

  if (type === "toy") {
    const toy = getToyOption(toyCode);
    const imageSrc = toyCode ? toyImageUrl(toyCode) : src;
    return (
      <div
        className={`flex h-full w-full flex-col items-center justify-center gap-3 bg-gradient-to-br from-ink-800/50 to-ink-700/40 p-3 ${className}`}
      >
        <img
          src={imageSrc}
          alt={toy?.name ?? "Игрушка"}
          loading="lazy"
          className={`max-h-full w-full rounded-2xl ${objectFit}`}
        />
      </div>
    );
  }

  if (type === "geopoint") {
    const point = geopoint ?? geopointFromMetadata(metadata);
    if (!point) {
      return (
        <div
          className={`flex h-full min-h-[10rem] w-full items-center justify-center bg-gradient-to-br from-ink-800/80 to-ink-700/70 p-6 ${className}`}
        >
          <p className="text-sm text-slate-400">Точка не задана</p>
        </div>
      );
    }
    const mapSrc = `https://www.openstreetmap.org/export/embed.html?bbox=${point.lng - 0.012}%2C${point.lat - 0.008}%2C${point.lng + 0.012}%2C${point.lat + 0.008}&layer=mapnik&marker=${point.lat}%2C${point.lng}`;
    return (
      <div
        className={`flex h-full min-h-[14rem] w-full flex-col overflow-hidden bg-ink-900 ${className}`}
      >
        <iframe
          title="Точка на карте"
          src={mapSrc}
          className="min-h-[12rem] w-full flex-1 border-0"
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
        />
        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-white/10 bg-ink-800/90 px-3 py-2.5">
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-slate-100">
              Точка на карте
            </p>
            <p className="text-[0.7rem] text-slate-400">
              {formatGeopointCoords(point)}
            </p>
          </div>
          <a
            href={osmMapUrl(point)}
            target="_blank"
            rel="noreferrer"
            className="inline-flex shrink-0 items-center gap-1.5 rounded-xl border border-white/15 bg-white/5 px-2.5 py-1.5 text-xs text-slate-200 transition hover:border-white/30 hover:bg-white/10"
          >
            <MapPin className="size-3.5" />
            Открыть
          </a>
        </div>
      </div>
    );
  }

  if (type === "question") {
    return (
      <QuestionPreview
        metadata={metadata}
        interactive={interactive}
        className={className}
      />
    );
  }

  return (
    <img
      src={src}
      alt=""
      loading="lazy"
      className={`h-full w-full ${objectFit} ${className}`}
    />
  );
}

function QuestionPreview({
  metadata,
  interactive,
  className = "",
}: {
  metadata?: Record<string, unknown> | null;
  interactive: boolean;
  className?: string;
}) {
  const quiz = questionFromMetadata(metadata);
  const [selected, setSelected] = useState<number | null>(null);

  if (!quiz) {
    return (
      <div
        className={`flex h-full min-h-[10rem] w-full items-center justify-center bg-gradient-to-br from-ink-800/80 to-ink-700/70 p-6 ${className}`}
      >
        <p className="text-sm text-slate-400">Вопрос не задан</p>
      </div>
    );
  }

  const answered = selected !== null;
  const correct = answered && selected === quiz.correct_index;

  return (
    <div
      className={`flex h-full min-h-[14rem] w-full flex-col justify-center gap-4 bg-gradient-to-br from-ink-800/90 to-ink-700/80 p-5 sm:p-7 ${className}`}
    >
      <p className="text-center text-base font-semibold leading-snug text-slate-100 sm:text-lg">
        {quiz.question}
      </p>
      <div className="mx-auto flex w-full max-w-md flex-col gap-2">
        {quiz.options.map((option, index) => {
          const isSelected = selected === index;
          const isCorrectOption = index === quiz.correct_index;
          let stateClass =
            "border-white/15 bg-white/[0.04] text-slate-200 hover:border-white/30 hover:bg-white/[0.08]";
          if (answered) {
            if (isCorrectOption) {
              stateClass =
                "border-emerald-400/50 bg-emerald-400/15 text-emerald-100";
            } else if (isSelected) {
              stateClass = "border-rose-400/45 bg-rose-400/15 text-rose-100";
            } else {
              stateClass = "border-white/10 bg-white/[0.02] text-slate-500";
            }
          } else if (isSelected) {
            stateClass =
              "border-glow-violet/50 bg-glow-violet/15 text-slate-100";
          }

          return (
            <button
              key={`${index}-${option}`}
              type="button"
              disabled={!interactive || answered}
              onClick={() => setSelected(index)}
              className={`flex w-full items-center gap-3 rounded-2xl border px-4 py-3 text-left text-sm font-medium transition disabled:cursor-default ${stateClass}`}
            >
              <span className="grid size-7 shrink-0 place-items-center rounded-full border border-current/30 text-xs font-bold">
                {answered && isCorrectOption ? (
                  <Check className="size-3.5" strokeWidth={3} />
                ) : answered && isSelected ? (
                  <X className="size-3.5" strokeWidth={3} />
                ) : (
                  index + 1
                )}
              </span>
              <span className="min-w-0 flex-1">{option}</span>
            </button>
          );
        })}
      </div>
      {answered ? (
        <p
          className={`text-center text-sm font-semibold ${
            correct ? "text-emerald-300" : "text-rose-300"
          }`}
        >
          {correct ? "Верно!" : "Неверно"}
        </p>
      ) : interactive ? (
        <p className="text-center text-xs text-slate-500">Выберите ответ</p>
      ) : (
        <p className="text-center text-xs text-slate-500">
          Правильный: {quiz.options[quiz.correct_index]}
        </p>
      )}
    </div>
  );
}
