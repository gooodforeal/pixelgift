import {
  CirclePlay,
  Loader2,
  RotateCcw,
  SwitchCamera,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { CirclePlayer } from "./CirclePlayer";

const MAX_RECORD_MS = 60_000;
const MIN_RECORD_MS = 800;
const HOLD_DELAY_MS = 280;
const OUTPUT_SIZE = 480;
const TARGET_FPS = 30;
const RING_RADIUS = 47;
const RING_LENGTH = 2 * Math.PI * RING_RADIUS;

const RECORDER_MIME_CANDIDATES = [
  "video/webm;codecs=vp8,opus",
  "video/webm;codecs=vp9,opus",
  "video/webm",
  "video/mp4;codecs=avc1.42E01E,mp4a.40.2",
  "video/mp4",
];

type Facing = "user" | "environment";
type Phase = "booting" | "live" | "recording" | "preview" | "error";

interface CircleRecorderProps {
  disabled?: boolean;
  uploading?: boolean;
  onSubmit: (blob: Blob) => void | Promise<void>;
}

function pickRecorderMime(): string {
  if (typeof MediaRecorder === "undefined") return "";
  return (
    RECORDER_MIME_CANDIDATES.find((type) =>
      MediaRecorder.isTypeSupported(type),
    ) ?? ""
  );
}

function cameraErrorMessage(error: unknown): string {
  if (!(error instanceof DOMException)) {
    return "Не удалось открыть камеру";
  }
  switch (error.name) {
    case "NotAllowedError":
    case "PermissionDeniedError":
      return "Нужен доступ к камере и микрофону";
    case "NotFoundError":
    case "DevicesNotFoundError":
      return "Камера не найдена";
    case "NotReadableError":
    case "TrackStartError":
      return "Камера занята другим приложением";
    case "SecurityError":
      return "Запись доступна только по HTTPS";
    default:
      return "Не удалось открыть камеру";
  }
}

function formatClock(ms: number): string {
  const total = Math.min(60, Math.max(0, Math.floor(ms / 1000)));
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

export function CircleRecorder({
  disabled = false,
  uploading = false,
  onSubmit,
}: CircleRecorderProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const cameraStreamRef = useRef<MediaStream | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const rafRef = useRef<number | null>(null);
  const facingRef = useRef<Facing>("user");
  const startedAtRef = useRef(0);
  const elapsedRef = useRef(0);
  const holdTimerRef = useRef<number | null>(null);
  const holdRecordingRef = useRef(false);
  const previewUrlRef = useRef<string | null>(null);
  const tickRef = useRef<number | null>(null);
  const phaseRef = useRef<Phase>("booting");
  const cancelledRef = useRef(false);

  const [phase, setPhase] = useState<Phase>("booting");
  const [facing, setFacing] = useState<Facing>("user");
  const [elapsedMs, setElapsedMs] = useState(0);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewBlob, setPreviewBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hint, setHint] = useState<string | null>(null);

  const setPhaseBoth = (next: Phase) => {
    phaseRef.current = next;
    setPhase(next);
  };

  const stopDrawLoop = () => {
    if (rafRef.current != null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
  };

  const stopCamera = () => {
    stopDrawLoop();
    const stream = cameraStreamRef.current;
    if (stream) {
      for (const track of stream.getTracks()) track.stop();
      cameraStreamRef.current = null;
    }
    const video = videoRef.current;
    if (video) {
      video.srcObject = null;
    }
  };

  const revokePreview = () => {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
      previewUrlRef.current = null;
    }
    setPreviewUrl(null);
    setPreviewBlob(null);
  };

  const startDrawLoop = () => {
    stopDrawLoop();
    const draw = () => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas?.getContext("2d");
      if (video && canvas && context && video.readyState >= 2) {
        const vw = video.videoWidth;
        const vh = video.videoHeight;
        if (vw && vh) {
          const side = Math.min(vw, vh);
          const sx = (vw - side) / 2;
          const sy = (vh - side) / 2;
          if (facingRef.current === "user") {
            context.save();
            context.translate(OUTPUT_SIZE, 0);
            context.scale(-1, 1);
            context.drawImage(
              video,
              sx,
              sy,
              side,
              side,
              0,
              0,
              OUTPUT_SIZE,
              OUTPUT_SIZE,
            );
            context.restore();
          } else {
            context.drawImage(
              video,
              sx,
              sy,
              side,
              side,
              0,
              0,
              OUTPUT_SIZE,
              OUTPUT_SIZE,
            );
          }
        }
      }
      rafRef.current = requestAnimationFrame(draw);
    };
    rafRef.current = requestAnimationFrame(draw);
  };

  const startCamera = async (nextFacing: Facing) => {
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new DOMException("Unsupported", "NotSupportedError");
    }
    stopCamera();
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: {
          facingMode: { ideal: nextFacing },
          width: { ideal: 720 },
          height: { ideal: 720 },
        },
      });
    } catch {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
          facingMode: { ideal: nextFacing },
          width: { ideal: 720 },
          height: { ideal: 720 },
        },
      });
      if (!cancelledRef.current) {
        setHint("Микрофон недоступен — кружок будет без звука");
      }
    }
    if (cancelledRef.current) {
      for (const track of stream.getTracks()) track.stop();
      return;
    }
    cameraStreamRef.current = stream;
    facingRef.current = nextFacing;
    const video = videoRef.current;
    if (!video) {
      for (const track of stream.getTracks()) track.stop();
      throw new Error("Video element missing");
    }
    video.srcObject = stream;
    await video.play();
    startDrawLoop();
  };

  const bootCamera = async (nextFacing: Facing = "user") => {
    setError(null);
    setHint(null);
    setPhaseBoth("booting");
    try {
      if (typeof MediaRecorder === "undefined") {
        setError(
          "Браузер не умеет записывать видео. Откройте в Chrome или Safari.",
        );
        setPhaseBoth("error");
        return;
      }
      if (cancelledRef.current) {
        stopCamera();
        return;
      }
      await startCamera(nextFacing);
      if (cancelledRef.current) {
        stopCamera();
        return;
      }
      setFacing(nextFacing);
      setPhaseBoth("live");
    } catch (caught) {
      setError(cameraErrorMessage(caught));
      setPhaseBoth("error");
    }
  };

  useEffect(() => {
    cancelledRef.current = false;
    void bootCamera("user");
    return () => {
      cancelledRef.current = true;
      if (holdTimerRef.current != null) {
        window.clearTimeout(holdTimerRef.current);
      }
      if (tickRef.current != null) {
        window.clearInterval(tickRef.current);
      }
      const recorder = recorderRef.current;
      if (recorder && recorder.state !== "inactive") {
        recorder.stop();
      }
      stopCamera();
      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current);
      }
    };
    // Mount/unmount only: camera is owned by this component.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const stopTicker = () => {
    if (tickRef.current != null) {
      window.clearInterval(tickRef.current);
      tickRef.current = null;
    }
  };

  const finishRecording = (blob: Blob) => {
    stopTicker();
    const duration = elapsedRef.current;
    if (duration < MIN_RECORD_MS) {
      setHint("Слишком коротко — нажмите и подержите кнопку записи");
      setElapsedMs(0);
      elapsedRef.current = 0;
      holdRecordingRef.current = false;
      setPhaseBoth("live");
      return;
    }
    stopCamera();
    revokePreview();
    const url = URL.createObjectURL(blob);
    previewUrlRef.current = url;
    setPreviewUrl(url);
    setPreviewBlob(blob);
    setHint(null);
    setPhaseBoth("preview");
  };

  const stopRecording = () => {
    const recorder = recorderRef.current;
    if (!recorder || recorder.state === "inactive") return;
    recorder.stop();
  };

  const startRecording = () => {
    if (disabled || uploading || phaseRef.current !== "live") return;
    const canvas = canvasRef.current;
    const camera = cameraStreamRef.current;
    if (!canvas || !camera) return;

    const mime = pickRecorderMime();
    let canvasStream: MediaStream;
    try {
      canvasStream = canvas.captureStream(TARGET_FPS);
    } catch {
      setError("Не удалось начать запись в этом браузере");
      setPhaseBoth("error");
      return;
    }

    const mixed = new MediaStream([
      ...canvasStream.getVideoTracks(),
      ...camera.getAudioTracks(),
    ]);
    const recorder = mime
      ? new MediaRecorder(mixed, {
          mimeType: mime,
          videoBitsPerSecond: 1_200_000,
        })
      : new MediaRecorder(mixed, { videoBitsPerSecond: 1_200_000 });

    chunksRef.current = [];
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data);
    };
    recorder.onerror = () => {
      setError("Запись прервалась. Попробуйте ещё раз.");
      setPhaseBoth("error");
      stopCamera();
    };
    recorder.onstop = () => {
      for (const track of canvasStream.getVideoTracks()) track.stop();
      recorderRef.current = null;
      const type = recorder.mimeType || mime || "video/webm";
      const blob = new Blob(chunksRef.current, { type });
      finishRecording(blob);
    };

    recorderRef.current = recorder;
    startedAtRef.current = performance.now();
    elapsedRef.current = 0;
    setElapsedMs(0);
    setHint(null);
    setPhaseBoth("recording");
    recorder.start(250);

    stopTicker();
    tickRef.current = window.setInterval(() => {
      const next = performance.now() - startedAtRef.current;
      elapsedRef.current = next;
      setElapsedMs(next);
      if (next >= MAX_RECORD_MS) {
        stopRecording();
      }
    }, 50);
  };

  const clearHoldTimer = () => {
    if (holdTimerRef.current != null) {
      window.clearTimeout(holdTimerRef.current);
      holdTimerRef.current = null;
    }
  };

  const onRecordPointerDown = (event: React.PointerEvent) => {
    if (disabled || uploading) return;
    if (phaseRef.current !== "live" && phaseRef.current !== "recording") return;
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);

    if (phaseRef.current === "recording") {
      if (!holdRecordingRef.current) stopRecording();
      return;
    }

    holdRecordingRef.current = false;
    clearHoldTimer();
    holdTimerRef.current = window.setTimeout(() => {
      holdTimerRef.current = null;
      holdRecordingRef.current = true;
      startRecording();
    }, HOLD_DELAY_MS);
  };

  const onRecordPointerUp = () => {
    const wasHoldTimer = holdTimerRef.current != null;
    clearHoldTimer();
    if (phaseRef.current === "live" && wasHoldTimer) {
      startRecording();
      return;
    }
    if (phaseRef.current === "recording" && holdRecordingRef.current) {
      holdRecordingRef.current = false;
      stopRecording();
    }
  };

  const switchCamera = () => {
    if (disabled || uploading || phase !== "live") return;
    const next: Facing = facing === "user" ? "environment" : "user";
    void bootCamera(next);
  };

  const retake = () => {
    revokePreview();
    setElapsedMs(0);
    elapsedRef.current = 0;
    void bootCamera(facingRef.current);
  };

  const submit = () => {
    if (!previewBlob || disabled || uploading) return;
    void onSubmit(previewBlob);
  };

  const progress = Math.min(1, elapsedMs / MAX_RECORD_MS);
  const busy = disabled || uploading;

  return (
    <div className="space-y-4 rounded-3xl border border-white/12 bg-white/[0.02] p-4 sm:p-5">
      <div className="flex items-center gap-2 text-sm font-semibold text-slate-100">
        <CirclePlay className="size-4 text-glow-violet" />
        Видеокружок
      </div>

      <div className="mx-auto flex w-full max-w-64 flex-col items-center gap-4">
        {phase === "preview" && previewUrl ? (
          <CirclePlayer src={previewUrl} className="w-full" />
        ) : null}
        <div
          className={`relative aspect-square w-full overflow-hidden rounded-full bg-ink-900 shadow-inner shadow-black/40 ${
            phase === "preview" ? "hidden" : ""
          }`}
          onPointerDown={onRecordPointerDown}
          onPointerUp={onRecordPointerUp}
          onPointerCancel={onRecordPointerUp}
          onContextMenu={(event) => event.preventDefault()}
          style={{ touchAction: "none" }}
        >
          <video
            ref={videoRef}
            playsInline
            muted
            autoPlay
            className="pointer-events-none absolute h-px w-px overflow-hidden opacity-0"
          />
          <canvas
            ref={canvasRef}
            width={OUTPUT_SIZE}
            height={OUTPUT_SIZE}
            className="h-full w-full object-cover"
          />
          {(phase === "recording" || phase === "live") && (
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
              {phase === "recording" ? (
                <circle
                  cx="50"
                  cy="50"
                  r={RING_RADIUS}
                  fill="none"
                  stroke="#f43f5e"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  strokeDasharray={RING_LENGTH}
                  strokeDashoffset={RING_LENGTH * (1 - progress)}
                  transform="rotate(-90 50 50)"
                />
              ) : null}
            </svg>
          )}
          {phase === "booting" || phase === "error" ? (
            <div className="absolute inset-0 grid place-items-center bg-ink-950/70 p-6 text-center">
              {phase === "booting" ? (
                <Loader2 className="size-8 animate-spin text-glow-violet" />
              ) : (
                <p className="text-sm leading-snug text-slate-200">{error}</p>
              )}
            </div>
          ) : null}
        </div>

        <div className="flex h-6 items-center gap-2 text-xs text-slate-400">
          {phase === "recording" ? (
            <>
              <span className="size-2 animate-pulse rounded-full bg-rose-500" />
              {formatClock(elapsedMs)} / 1:00
            </>
          ) : phase === "live" ? (
            "0:00 / 1:00"
          ) : phase === "preview" ? (
            "Нажмите, чтобы посмотреть"
          ) : null}
        </div>
      </div>

      {hint ? <p className="text-center text-xs text-amber-200">{hint}</p> : null}

      {phase === "error" ? (
        <div className="flex justify-end">
          <button
            type="button"
            className="btn-primary px-5 py-2.5 text-sm"
            disabled={busy}
            onClick={() => void bootCamera(facingRef.current)}
          >
            Повторить
          </button>
        </div>
      ) : phase === "preview" ? (
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-slate-400">
            Кружок сохранится как видео и откроется в подарке
          </p>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="btn-ghost px-4 py-2 text-sm"
              disabled={busy}
              onClick={retake}
            >
              <RotateCcw className="size-4" />
              Переснять
            </button>
            <button
              type="button"
              className="btn-primary px-5 py-2.5 text-sm"
              disabled={busy || !previewBlob}
              onClick={submit}
            >
              {uploading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Сохраняем…
                </>
              ) : (
                "Добавить кружок"
              )}
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-slate-400">
            Удерживайте кнопку или нажмите, чтобы записать до 60 секунд
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              className="btn-ghost px-3 py-2 text-sm"
              disabled={busy || phase !== "live"}
              onClick={switchCamera}
              aria-label="Сменить камеру"
            >
              <SwitchCamera className="size-4" />
            </button>
            <button
              type="button"
              aria-label={
                phase === "recording" ? "Остановить запись" : "Записать кружок"
              }
              disabled={busy || (phase !== "live" && phase !== "recording")}
              onPointerDown={onRecordPointerDown}
              onPointerUp={onRecordPointerUp}
              onPointerCancel={onRecordPointerUp}
              onContextMenu={(event) => event.preventDefault()}
              className={`grid size-14 place-items-center rounded-full border-4 transition ${
                phase === "recording"
                  ? "border-rose-300 bg-rose-500 shadow-[0_0_0_6px_rgb(244_63_94_/_0.25)]"
                  : "border-white/30 bg-rose-500 hover:bg-rose-400"
              } disabled:opacity-50`}
              style={{ touchAction: "none" }}
            >
              <span
                className={`bg-white transition-all ${
                  phase === "recording"
                    ? "size-5 rounded-md"
                    : "size-11 rounded-full"
                }`}
              />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
