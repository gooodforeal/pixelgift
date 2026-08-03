import { motion } from "framer-motion";

import { useCountdown } from "../hooks/useCountdown";
import { pluralize } from "../lib/format";

interface CountdownTimerProps {
  activatesAt: string;
  accent?: string;
  compact?: boolean;
  onFinish?: () => void;
}

export function CountdownTimer({
  activatesAt,
  accent = "#a855f7",
  compact = false,
  onFinish,
}: CountdownTimerProps) {
  const { days, hours, minutes, seconds } = useCountdown(activatesAt, onFinish);

  const cells: Array<{ value: number; label: string }> = [
    { value: days, label: pluralize(days, ["день", "дня", "дней"]) },
    { value: hours, label: pluralize(hours, ["час", "часа", "часов"]) },
    { value: minutes, label: pluralize(minutes, ["минута", "минуты", "минут"]) },
    { value: seconds, label: pluralize(seconds, ["секунда", "секунды", "секунд"]) },
  ];

  if (compact) {
    return (
      <span className="font-mono text-sm text-slate-300 tabular-nums">
        {days}д {String(hours).padStart(2, "0")}:{String(minutes).padStart(2, "0")}:
        {String(seconds).padStart(2, "0")}
      </span>
    );
  }

  return (
    <div className="flex flex-wrap justify-center gap-3 sm:gap-4">
      {cells.map((cell, index) => (
        <motion.div
          key={cell.label}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.08 }}
          className="glass-soft min-w-[5.5rem] px-4 py-3 text-center sm:min-w-[6.5rem]"
          style={{ borderColor: `${accent}33` }}
        >
          <div
            className="font-display text-3xl leading-none tabular-nums sm:text-4xl"
            style={{ color: accent }}
          >
            {String(cell.value).padStart(2, "0")}
          </div>
          <div className="mt-1.5 text-[0.65rem] tracking-wide text-slate-400 uppercase">
            {cell.label}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
