import { useCallback, useEffect, useRef, useState } from "react";
import { Eraser } from "lucide-react";

interface ScratchRevealProps {
  children: React.ReactNode;
  className?: string;
  /** Fraction of pixels that must be cleared before reveal completes (0–1). */
  revealThreshold?: number;
  accent?: string;
  onRevealed?: () => void;
}

const COVER_COLOR = "#1a1528";
const COVER_PATTERN = "#2a2340";

export function ScratchReveal({
  children,
  className = "",
  revealThreshold = 0.42,
  accent = "#c4b5fd",
  onRevealed,
}: ScratchRevealProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const dprRef = useRef(1);
  const logicalSizeRef = useRef({ w: 0, h: 0 });
  const drawingRef = useRef(false);
  const lastPointRef = useRef<{ x: number; y: number } | null>(null);
  const revealedRef = useRef(false);
  const onRevealedRef = useRef(onRevealed);
  onRevealedRef.current = onRevealed;

  const [hintVisible, setHintVisible] = useState(true);
  const [revealed, setRevealed] = useState(false);

  const paintCover = useCallback((ctx: CanvasRenderingContext2D, width: number, height: number) => {
    // Bleed past edges so subpixel layout never leaves a gap.
    // Caller must already set the DPR transform — paint in CSS pixels.
    const pad = 2;
    ctx.globalCompositeOperation = "source-over";
    ctx.fillStyle = COVER_COLOR;
    ctx.fillRect(-pad, -pad, width + pad * 2, height + pad * 2);

    ctx.fillStyle = COVER_PATTERN;
    const step = Math.max(10, Math.round(Math.min(width, height) / 28));
    for (let y = 0; y < height; y += step) {
      for (let x = 0; x < width; x += step) {
        if ((x / step + y / step) % 2 === 0) {
          ctx.globalAlpha = 0.35;
          ctx.fillRect(x, y, step * 0.7, step * 0.7);
        }
      }
    }
    ctx.globalAlpha = 1;

    const gradient = ctx.createRadialGradient(
      width * 0.5,
      height * 0.45,
      Math.min(width, height) * 0.08,
      width * 0.5,
      height * 0.5,
      Math.max(width, height) * 0.65,
    );
    gradient.addColorStop(0, "rgba(255,255,255,0.08)");
    gradient.addColorStop(1, "rgba(0,0,0,0.35)");
    ctx.fillStyle = gradient;
    ctx.fillRect(-pad, -pad, width + pad * 2, height + pad * 2);
  }, []);

  const resizeCanvas = useCallback(() => {
    const wrap = wrapRef.current;
    const canvas = canvasRef.current;
    if (!wrap || !canvas || revealedRef.current) return;

    const rect = wrap.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    // ceil — never undersize vs fractional layout boxes
    const w = Math.max(1, Math.ceil(rect.width));
    const h = Math.max(1, Math.ceil(rect.height));
    if (w < 2 || h < 2) return;

    dprRef.current = dpr;
    logicalSizeRef.current = { w, h };

    canvas.width = Math.ceil(w * dpr);
    canvas.height = Math.ceil(h * dpr);
    // Stretch to parent so CSS box always matches the wrap (no 1px gaps).
    canvas.style.width = "100%";
    canvas.style.height = "100%";

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    paintCover(ctx, w, h);
  }, [paintCover]);

  useEffect(() => {
    resizeCanvas();
    const wrap = wrapRef.current;
    if (!wrap || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(() => resizeCanvas());
    observer.observe(wrap);
    return () => observer.disconnect();
  }, [resizeCanvas]);

  const sampleClearedRatio = useCallback(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d", { willReadFrequently: true });
    if (!canvas || !ctx) return 0;

    const { width, height } = canvas;
    const sampleStep = 8;
    let cleared = 0;
    let total = 0;
    const data = ctx.getImageData(0, 0, width, height).data;

    for (let y = 0; y < height; y += sampleStep) {
      for (let x = 0; x < width; x += sampleStep) {
        const alpha = data[(y * width + x) * 4 + 3];
        total += 1;
        if (alpha < 40) cleared += 1;
      }
    }
    return total === 0 ? 0 : cleared / total;
  }, []);

  const finishIfReady = useCallback(() => {
    if (revealedRef.current) return;
    if (sampleClearedRatio() < revealThreshold) return;

    revealedRef.current = true;
    setRevealed(true);
    setHintVisible(false);
    onRevealedRef.current?.();
  }, [revealThreshold, sampleClearedRatio]);

  const pointFromEvent = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return null;
    const { w, h } = logicalSizeRef.current;
    return {
      x: ((event.clientX - rect.left) / rect.width) * w,
      y: ((event.clientY - rect.top) / rect.height) * h,
    };
  };

  const eraseAt = (from: { x: number; y: number } | null, to: { x: number; y: number }) => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const { w, h } = logicalSizeRef.current;
    const brush = Math.max(64, Math.min(w, h) * 0.28);
    ctx.setTransform(dprRef.current, 0, 0, dprRef.current, 0, 0);
    ctx.globalCompositeOperation = "destination-out";
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.lineWidth = brush;
    ctx.beginPath();
    if (from) {
      ctx.moveTo(from.x, from.y);
      ctx.lineTo(to.x, to.y);
    } else {
      ctx.moveTo(to.x, to.y);
      ctx.lineTo(to.x + 0.01, to.y);
    }
    ctx.stroke();
  };

  const onPointerDown = (event: React.PointerEvent<HTMLCanvasElement>) => {
    if (revealedRef.current) return;
    const point = pointFromEvent(event);
    if (!point) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    drawingRef.current = true;
    lastPointRef.current = point;
    setHintVisible(false);
    eraseAt(null, point);
  };

  const onPointerMove = (event: React.PointerEvent<HTMLCanvasElement>) => {
    if (!drawingRef.current || revealedRef.current) return;
    const point = pointFromEvent(event);
    if (!point) return;
    eraseAt(lastPointRef.current, point);
    lastPointRef.current = point;
  };

  const onPointerUp = () => {
    if (!drawingRef.current) return;
    drawingRef.current = false;
    lastPointRef.current = null;
    finishIfReady();
  };

  return (
    <div
      ref={wrapRef}
      className={`relative isolate inline-grid max-h-full max-w-full overflow-hidden ${className}`}
    >
      <div className="col-start-1 row-start-1 min-h-0 min-w-0 select-none [&_img]:block [&_img]:max-h-[min(58dvh,32rem)] [&_img]:max-w-full [&_img]:h-auto [&_img]:w-auto">
        {children}
      </div>

      {!revealed && (
        <canvas
          ref={canvasRef}
          className="col-start-1 row-start-1 z-10 block h-full w-full touch-none cursor-crosshair"
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerCancel={onPointerUp}
          aria-label="Сотрите слой, чтобы увидеть фото"
        />
      )}

      {hintVisible && !revealed && (
        <div className="pointer-events-none col-start-1 row-start-1 z-20 flex items-center justify-center p-4">
          <div
            className="flex max-w-[16rem] flex-col items-center gap-2 rounded-2xl px-4 py-3 text-center backdrop-blur-sm"
            style={{
              background: "rgb(10 8 20 / 0.55)",
              boxShadow: `0 0 0 1px ${accent}33`,
            }}
          >
            <Eraser className="size-5" style={{ color: accent }} />
            <p className="text-sm font-medium text-white/95">Сотри слой ластиком</p>
            <p className="text-[0.7rem] leading-snug text-white/65">
              Проведи пальцем или мышью, чтобы увидеть фото
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
