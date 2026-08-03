import { useMemo } from "react";
import { motion } from "framer-motion";

interface ConfettiBurstProps {
  colors?: string[];
  count?: number;
}

export function ConfettiBurst({
  colors = ["#f472b6", "#a855f7", "#22d3ee", "#fbbf24", "#34d399"],
  count = 70,
}: ConfettiBurstProps) {
  const pieces = useMemo(
    () =>
      Array.from({ length: count }, (_, index) => ({
        id: index,
        color: colors[index % colors.length],
        angle: (index / count) * Math.PI * 2,
        distance: 180 + ((index * 29) % 320),
        size: 6 + ((index * 5) % 9),
        duration: 1.4 + ((index * 7) % 10) / 10,
      })),
    [colors, count],
  );

  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 z-50 overflow-hidden">
      {pieces.map((piece) => (
        <motion.span
          key={piece.id}
          className="absolute top-1/2 left-1/2 rounded-[2px]"
          style={{
            width: piece.size,
            height: piece.size * 1.6,
            background: piece.color,
          }}
          initial={{ x: 0, y: 0, opacity: 1, rotate: 0 }}
          animate={{
            x: Math.cos(piece.angle) * piece.distance,
            y: Math.sin(piece.angle) * piece.distance + 220,
            opacity: 0,
            rotate: 540,
          }}
          transition={{ duration: piece.duration, ease: "easeOut" }}
        />
      ))}
    </div>
  );
}
