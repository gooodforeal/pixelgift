import { Eraser, Loader2, Palette } from "lucide-react";
import { useEffect, useRef, useState } from "react";

const CANVAS_SIZE = 1024;
const BRUSH_COLORS = [
  "#111827",
  "#7c3aed",
  "#ec4899",
  "#0ea5e9",
  "#22c55e",
  "#f59e0b",
] as const;

interface DrawingCanvasProps {
  disabled?: boolean;
  uploading?: boolean;
  onSubmit: (blob: Blob) => void | Promise<void>;
}

export function DrawingCanvas({
  disabled = false,
  uploading = false,
  onSubmit,
}: DrawingCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawingRef = useRef(false);
  const lastPointRef = useRef<{ x: number; y: number } | null>(null);

  const [brushColor, setBrushColor] = useState<string>(BRUSH_COLORS[0]);
  const [brushSize, setBrushSize] = useState(8);
  const [hasDrawing, setHasDrawing] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.width = CANVAS_SIZE;
    canvas.height = CANVAS_SIZE;

    const context = canvas.getContext("2d");
    if (!context) return;

    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.lineCap = "round";
    context.lineJoin = "round";
  }, []);

  const getContext = () => canvasRef.current?.getContext("2d") ?? null;

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const context = getContext();
    if (!canvas || !context) return;
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, canvas.width, canvas.height);
    setHasDrawing(false);
  };

  const getPoint = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return null;
    return {
      x: ((event.clientX - rect.left) / rect.width) * canvas.width,
      y: ((event.clientY - rect.top) / rect.height) * canvas.height,
    };
  };

  const startDrawing = (event: React.PointerEvent<HTMLCanvasElement>) => {
    if (disabled || uploading) return;
    const point = getPoint(event);
    const context = getContext();
    if (!point || !context) return;

    drawingRef.current = true;
    lastPointRef.current = point;
    context.beginPath();
    context.fillStyle = brushColor;
    context.arc(point.x, point.y, Math.max(brushSize / 2, 1), 0, Math.PI * 2);
    context.fill();
    setHasDrawing(true);
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const draw = (event: React.PointerEvent<HTMLCanvasElement>) => {
    if (!drawingRef.current) return;
    const point = getPoint(event);
    const context = getContext();
    const lastPoint = lastPointRef.current;
    if (!point || !context || !lastPoint) return;

    context.strokeStyle = brushColor;
    context.lineWidth = brushSize;
    context.beginPath();
    context.moveTo(lastPoint.x, lastPoint.y);
    context.lineTo(point.x, point.y);
    context.stroke();
    lastPointRef.current = point;
    setHasDrawing(true);
  };

  const stopDrawing = (event?: React.PointerEvent<HTMLCanvasElement>) => {
    drawingRef.current = false;
    lastPointRef.current = null;
    if (event && event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  };

  const submit = () => {
    const canvas = canvasRef.current;
    if (!canvas || disabled || uploading || !hasDrawing) return;
    canvas.toBlob((blob) => {
      if (blob) void onSubmit(blob);
    }, "image/png");
  };

  return (
    <div className="space-y-4 rounded-3xl border border-white/12 bg-white/[0.02] p-4 sm:p-5">
      <div className="flex items-center gap-2 text-sm font-semibold text-slate-100">
        <Palette className="size-4 text-glow-violet" />
        Рисунок на холсте
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex flex-wrap items-center gap-2">
          {BRUSH_COLORS.map((color) => {
            const selected = color === brushColor;
            return (
              <button
                key={color}
                type="button"
                aria-label={`Цвет ${color}`}
                disabled={disabled || uploading}
                onClick={() => setBrushColor(color)}
                className={`size-8 rounded-full border transition ${
                  selected ? "scale-110 border-white/80" : "border-white/20"
                }`}
                style={{ backgroundColor: color }}
              />
            );
          })}
        </div>

        <label className="ml-auto flex items-center gap-2 text-xs text-slate-300">
          Кисть
          <input
            type="range"
            min={2}
            max={24}
            step={1}
            value={brushSize}
            disabled={disabled || uploading}
            onChange={(event) => setBrushSize(Number(event.target.value))}
          />
          <span className="w-6 text-right">{brushSize}</span>
        </label>
      </div>

      <div className="mx-auto w-full max-w-56 overflow-hidden rounded-3xl border border-white/12 bg-white shadow-inner shadow-black/30 sm:max-w-64">
        <canvas
          ref={canvasRef}
          className="block aspect-square w-full touch-none"
          onPointerDown={startDrawing}
          onPointerMove={draw}
          onPointerUp={stopDrawing}
          onPointerLeave={stopDrawing}
          onPointerCancel={stopDrawing}
        />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-xs text-slate-400">
          Рисунок сохранится как PNG и появится в подарке как отдельная карточка
        </p>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="btn-ghost px-4 py-2 text-sm"
            disabled={disabled || uploading || !hasDrawing}
            onClick={clearCanvas}
          >
            <Eraser className="size-4" />
            Очистить
          </button>
          <button
            type="button"
            className="btn-primary px-5 py-2.5 text-sm"
            disabled={disabled || uploading || !hasDrawing}
            onClick={submit}
          >
            {uploading ? (
              <>
                <Loader2 className="size-4 animate-spin" />
                Сохраняем…
              </>
            ) : (
              "Добавить рисунок"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
