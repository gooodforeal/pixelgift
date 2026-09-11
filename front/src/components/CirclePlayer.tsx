import { Pause, Play } from "lucide-react";
import { useEffect, useRef, useState } from "react";

const RING_RADIUS = 47;
const RING_LENGTH = 2 * Math.PI * RING_RADIUS;

interface CirclePlayerProps {
  src: string;
  className?: string;
  /** Editor thumbs can render a still circular crop without playback. */
  interactive?: boolean;
}

export function CirclePlayer({
  src,
  className = "",
  interactive = true,
}: CirclePlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    setPlaying(false);
    setProgress(0);
    const video = videoRef.current;
    if (video) {
      video.pause();
      video.currentTime = 0;
    }
  }, [src]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const onTime = () => {
      const duration = video.duration;
      if (!Number.isFinite(duration) || duration <= 0) {
        setProgress(0);
        return;
      }
      setProgress(video.currentTime / duration);
    };
    const onPlay = () => setPlaying(true);
    const onPause = () => setPlaying(false);
    const onEnded = () => {
      setPlaying(false);
      setProgress(0);
      video.currentTime = 0;
    };

    video.addEventListener("timeupdate", onTime);
    video.addEventListener("play", onPlay);
    video.addEventListener("pause", onPause);
    video.addEventListener("ended", onEnded);
    return () => {
      video.removeEventListener("timeupdate", onTime);
      video.removeEventListener("play", onPlay);
      video.removeEventListener("pause", onPause);
      video.removeEventListener("ended", onEnded);
    };
  }, [src]);

  const toggle = () => {
    const video = videoRef.current;
    if (!video || !interactive) return;
    if (video.paused) void video.play();
    else video.pause();
  };

  return (
    <div
      className={`relative aspect-square overflow-hidden rounded-full bg-ink-900 ${className}`}
    >
      <video
        ref={videoRef}
        src={src}
        playsInline
        preload="metadata"
        muted={!interactive}
        className="h-full w-full object-cover"
      />
      {interactive ? (
        <>
          <svg
            viewBox="0 0 100 100"
            className="pointer-events-none absolute inset-0 h-full w-full"
            aria-hidden
          >
            <circle
              cx="50"
              cy="50"
              r={RING_RADIUS}
              fill="none"
              stroke="rgba(255,255,255,0.22)"
              strokeWidth="3.5"
            />
            <circle
              cx="50"
              cy="50"
              r={RING_RADIUS}
              fill="none"
              stroke="white"
              strokeWidth="3.5"
              strokeLinecap="round"
              strokeDasharray={RING_LENGTH}
              strokeDashoffset={RING_LENGTH * (1 - progress)}
              transform="rotate(-90 50 50)"
            />
          </svg>
          <button
            type="button"
            onClick={toggle}
            aria-label={playing ? "Пауза" : "Смотреть кружок"}
            className="absolute inset-0 grid place-items-center"
          >
            {!playing ? (
              <span className="grid size-14 place-items-center rounded-full bg-black/45 text-white backdrop-blur-sm">
                <Play className="size-7 translate-x-0.5 fill-current" />
              </span>
            ) : (
              <span className="sr-only">Пауза</span>
            )}
          </button>
          {playing ? (
            <span className="pointer-events-none absolute inset-0 grid place-items-center opacity-0 transition-opacity hover:opacity-100">
              <span className="grid size-14 place-items-center rounded-full bg-black/45 text-white">
                <Pause className="size-7 fill-current" />
              </span>
            </span>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
