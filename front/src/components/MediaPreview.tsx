import { MapPin } from "lucide-react";

import type { BoxItemType } from "../lib/types";
import {
  formatGeopointCoords,
  geopointFromMetadata,
  osmMapUrl,
  type GeopointCoords,
} from "../lib/geopoint";
import { getToyOption, toyImageUrl } from "../lib/toys";

interface MediaPreviewProps {
  src: string;
  type: BoxItemType;
  className?: string;
  /** `cover` crops to fill; `contain` shows the whole media (default for gift reveal). */
  fit?: "cover" | "contain";
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
  caption,
  toyCode,
  geopoint,
  metadata,
}: MediaPreviewProps) {
  const objectFit = fit === "cover" ? "object-cover" : "object-contain";

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

  return (
    <img
      src={src}
      alt=""
      loading="lazy"
      className={`h-full w-full ${objectFit} ${className}`}
    />
  );
}
