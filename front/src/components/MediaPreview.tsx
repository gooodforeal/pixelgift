import type { BoxItemType } from "../lib/types";
import { getToyOption, toyImageUrl } from "../lib/toys";

interface MediaPreviewProps {
  src: string;
  type: BoxItemType;
  className?: string;
  /** `cover` crops to fill; `contain` shows the whole media (default for gift reveal). */
  fit?: "cover" | "contain";
  caption?: string | null;
  toyCode?: string | null;
}

export function MediaPreview({
  src,
  type,
  className = "",
  fit = "contain",
  caption,
  toyCode,
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

  return (
    <img
      src={src}
      alt=""
      loading="lazy"
      className={`h-full w-full ${objectFit} ${className}`}
    />
  );
}
