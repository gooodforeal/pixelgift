import { useMemo } from "react";
import { motion } from "framer-motion";

import { PARTICLE_GLYPHS, type ParticleKind } from "../lib/particles";

interface ParticlesProps {
  particle: ParticleKind;
  accent: string;
  count?: number;
}

export function Particles({ particle, accent, count = 26 }: ParticlesProps) {
  const glyphs = PARTICLE_GLYPHS[particle] ?? PARTICLE_GLYPHS.sparkle;
  const items = useMemo(
    () =>
      Array.from({ length: count }, (_, index) => ({
        id: index,
        glyph: glyphs[index % glyphs.length],
        left: (index * 37) % 100,
        size: 10 + ((index * 13) % 20),
        duration: 11 + ((index * 7) % 12),
        delay: -((index * 3) % 14),
        drift: index % 2 === 0 ? 40 : -40,
      })),
    [count, glyphs],
  );

  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      {items.map((item) => (
        <motion.span
          key={item.id}
          className="absolute top-0 select-none"
          style={{
            left: `${item.left}%`,
            fontSize: item.size,
            color: accent,
            opacity: 0.5,
          }}
          initial={{ y: "-10vh" }}
          animate={{ y: "110vh", x: [0, item.drift, 0], rotate: [0, 180, 360] }}
          transition={{
            duration: item.duration,
            delay: item.delay,
            repeat: Infinity,
            ease: "linear",
          }}
        >
          {item.glyph}
        </motion.span>
      ))}
    </div>
  );
}
