import { useId } from "react";
import { motion } from "framer-motion";

import type { ThemeConfig } from "../lib/types";

export type GiftBoxPalette = {
  body: string;
  bodyDark: string;
  lid: string;
  lidLight: string;
  ribbon: string;
  ribbonDark: string;
  glow: string;
};

export function resolveGiftBoxPalette(
  giftBox: ThemeConfig["gift_box"] | null | undefined,
  gradient: string[],
  accent: string,
): GiftBoxPalette {
  const override = giftBox ?? {};
  const body = override.body ?? gradient[1] ?? "#f0a8c8";
  const lid = override.lid ?? body;
  return {
    body,
    bodyDark: override.bodyDark ?? gradient[0] ?? body,
    lid,
    lidLight: override.lidLight ?? lid,
    ribbon: override.ribbon ?? accent,
    ribbonDark: override.ribbonDark ?? accent,
    glow: `${accent}55`,
  };
}

const SHADE = "rgb(6 4 20 / 0.2)";

interface GiftBox3DProps {
  palette: GiftBoxPalette;
  opening?: boolean;
  isOpen?: boolean;
  size?: "md" | "lg";
  className?: string;
}

export function GiftBox3D({
  palette,
  opening = false,
  isOpen = false,
  size = "lg",
  className = "",
}: GiftBox3DProps) {
  const lidOpen = isOpen || opening;
  const uid = useId().replace(/:/g, "");
  const px = size === "lg" ? 288 : 220;

  const lidTop = `gb-lid-${uid}`;
  const faceLeft = `gb-left-${uid}`;
  const faceRight = `gb-right-${uid}`;
  const satin = `gb-satin-${uid}`;
  const cavity = `gb-cavity-${uid}`;

  return (
    <div className={`gift-box-scene ${className}`}>
      {opening && (
        <motion.div
          className="gift-box__burst"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: [0, 0.9, 0], scale: [0.5, 1.4, 1.8] }}
          transition={{ duration: 0.95, ease: "easeOut" }}
          style={{
            background: `radial-gradient(circle, ${palette.lidLight} 0%, ${palette.glow} 48%, transparent 72%)`,
          }}
        />
      )}

      <motion.div
        className="gift-box"
        animate={
          lidOpen ? { rotate: 0, y: -4 } : { rotate: [-2.5, 2.5, -2.5], y: [0, -9, 0] }
        }
        transition={
          lidOpen
            ? { duration: 0.5, ease: [0.22, 1, 0.36, 1] }
            : { duration: 6, repeat: Infinity, ease: "easeInOut" }
        }
      >
        <svg viewBox="0 0 240 252" width={px} height={px * (252 / 240)} role="img">
          <defs>
            <linearGradient id={lidTop} x1="0.1" y1="0" x2="0.8" y2="1">
              <stop offset="0%" stopColor={palette.lidLight} />
              <stop offset="100%" stopColor={palette.lid} />
            </linearGradient>
            <linearGradient id={faceLeft} x1="0" y1="0" x2="0.4" y2="1">
              <stop offset="0%" stopColor={palette.body} />
              <stop offset="100%" stopColor={palette.bodyDark} />
            </linearGradient>
            <linearGradient id={faceRight} x1="1" y1="0" x2="0.3" y2="1">
              <stop offset="0%" stopColor={palette.body} />
              <stop offset="100%" stopColor={palette.bodyDark} />
            </linearGradient>
            <linearGradient id={satin} x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor={palette.ribbonDark} />
              <stop offset="42%" stopColor={palette.ribbon} />
              <stop offset="100%" stopColor={palette.ribbonDark} />
            </linearGradient>
            <radialGradient id={cavity} cx="0.5" cy="0.5" r="0.6">
              <stop offset="0%" stopColor={palette.lidLight} stopOpacity="0.75" />
              <stop offset="100%" stopColor="#0b0718" stopOpacity="0.9" />
            </radialGradient>
          </defs>

          <ellipse cx="120" cy="221" rx="64" ry="11" fill="rgb(4 2 16 / 0.22)" />

          {/* Корпус */}
          <g strokeLinejoin="round" strokeWidth="5">
            <polygon
              points="60,120 120,88 180,120 120,152"
              fill={lidOpen ? `url(#${cavity})` : `url(#${lidTop})`}
              stroke={lidOpen ? "#0b0718" : palette.lid}
            />
            <polygon
              points="60,120 120,152 120,214 60,182"
              fill={`url(#${faceLeft})`}
              stroke={palette.body}
            />
            <polygon
              points="120,152 180,120 180,182 120,214"
              fill={`url(#${faceRight})`}
              stroke={palette.body}
            />
            <polygon points="120,152 180,120 180,182 120,214" fill={SHADE} stroke={SHADE} />
          </g>

          {/* Лента на корпусе */}
          <g strokeLinejoin="round" strokeWidth="1.5" stroke={palette.ribbonDark}>
            <polygon points="76,128 96,139 96,201 76,190" fill={`url(#${satin})`} />
            <polygon points="144,139 164,128 164,190 144,201" fill={`url(#${satin})`} />
            <polygon points="144,139 164,128 164,190 144,201" fill={SHADE} stroke="none" />
          </g>

          {/* Крышка */}
          <motion.g
            animate={{
              y: lidOpen ? -78 : 0,
              x: lidOpen ? -14 : 0,
              rotate: lidOpen ? -17 : 0,
            }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
            style={{ transformOrigin: "120px 140px" }}
          >
            <g strokeLinejoin="round" strokeWidth="5">
              <polygon
                points="52,116 120,80 188,116 120,152"
                fill={`url(#${lidTop})`}
                stroke={palette.lidLight}
              />
              <polygon
                points="52,116 120,152 120,170 52,134"
                fill={`url(#${faceLeft})`}
                stroke={palette.body}
              />
              <polygon
                points="120,152 188,116 188,134 120,170"
                fill={`url(#${faceRight})`}
                stroke={palette.body}
              />
              <polygon points="120,152 188,116 188,134 120,170" fill={SHADE} stroke={SHADE} />
            </g>

            {/* Лента на крышке */}
            <g strokeLinejoin="round" strokeWidth="1.5" stroke={palette.ribbonDark}>
              <polygon points="76,129 144,93 164,103 96,139" fill={`url(#${satin})`} />
              <polygon points="76,103 96,93 164,129 144,139" fill={`url(#${satin})`} />
              <polygon points="76,129 96,139 96,157 76,147" fill={`url(#${satin})`} />
              <polygon points="144,139 164,129 164,147 144,157" fill={`url(#${satin})`} />
              <polygon points="144,139 164,129 164,147 144,157" fill={SHADE} stroke="none" />
            </g>

            {/* Бант */}
            <g transform="translate(120 106)" stroke={palette.ribbonDark} strokeWidth="2">
              <ellipse
                rx="20"
                ry="13"
                transform="translate(-19 -9) rotate(-24)"
                fill={`url(#${satin})`}
              />
              <ellipse
                rx="20"
                ry="13"
                transform="translate(19 -9) rotate(24)"
                fill={`url(#${satin})`}
              />
              <ellipse rx="9.5" ry="8" cy="-1" fill={palette.ribbonDark} />
              <ellipse rx="4" ry="3" cy="-3.5" fill={palette.ribbon} stroke="none" opacity="0.55" />
            </g>
          </motion.g>
        </svg>
      </motion.div>
    </div>
  );
}
