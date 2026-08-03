import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Image as ImageIcon, Play } from "lucide-react";

import { GiftBox3D, resolveGiftBoxPalette } from "./GiftBox3D";
import { Particles } from "./Particles";
import { radialGlowCss, resolveTheme, themeBackgroundLayers } from "../lib/theme";
import type { BoxDesign } from "../lib/types";

type PreviewPhase = "idle" | "open" | "reveal" | "content";

const PHASE_MS: Record<Exclude<PreviewPhase, "idle">, number> = {
  open: 1000,
  reveal: 1500,
  content: 2800,
};

function sleep(ms: number) {
  return new Promise<void>((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

interface DesignGiftPreviewProps {
  design: BoxDesign;
}

export function DesignGiftPreview({ design }: DesignGiftPreviewProps) {
  const theme = resolveTheme(design);
  const giftPalette = useMemo(
    () => resolveGiftBoxPalette(theme.gift_box, theme.gradient, theme.accent),
    [theme.gift_box, theme.gradient, theme.accent],
  );
  const [phase, setPhase] = useState<PreviewPhase>("idle");
  const [burst, setBurst] = useState(false);
  const playingRef = useRef(false);
  const bgLayers = themeBackgroundLayers(theme);
  const isIdle = phase === "idle";

  useEffect(() => {
    setPhase("idle");
    setBurst(false);
    playingRef.current = false;
  }, [design.code, design.id]);

  async function playAnimation() {
    if (playingRef.current) return;
    playingRef.current = true;

    setPhase("open");
    setBurst(true);
    window.setTimeout(() => setBurst(false), 700);
    await sleep(PHASE_MS.open);

    if (!playingRef.current) return;
    setPhase("reveal");
    await sleep(PHASE_MS.reveal);

    if (!playingRef.current) return;
    setPhase("content");
    await sleep(PHASE_MS.content);

    if (!playingRef.current) return;
    setPhase("idle");
    playingRef.current = false;
  }

  return (
    <div
      className="relative h-full w-full overflow-hidden"
      style={{
        ...bgLayers,
        color: theme.text,
      }}
    >
      {theme.background_image_url ? (
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{ background: "linear-gradient(165deg, rgb(0 0 0 / 0.5), rgb(0 0 0 / 0.3))" }}
        />
      ) : null}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{ background: radialGlowCss(theme.accent) }}
      />
      <Particles particle={theme.particle} accent={theme.accent} count={10} />

      {burst && (
        <div aria-hidden className="pointer-events-none absolute inset-0 z-20">
          {Array.from({ length: 18 }, (_, index) => {
            const angle = (index / 18) * Math.PI * 2;
            const distance = 70 + (index % 5) * 14;
            return (
              <motion.span
                key={index}
                className="absolute top-1/2 left-1/2 size-1.5 rounded-sm"
                style={{ background: theme.accent }}
                initial={{ x: 0, y: 0, opacity: 1 }}
                animate={{
                  x: Math.cos(angle) * distance,
                  y: Math.sin(angle) * distance,
                  opacity: 0,
                }}
                transition={{ duration: 0.75, ease: "easeOut" }}
              />
            );
          })}
        </div>
      )}

      <div className="relative flex h-full flex-col items-center justify-center px-4 pb-6 text-center">
        <AnimatePresence mode="wait">
          {phase === "content" ? (
            <motion.div
              key="content"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="w-full space-y-2"
            >
              <div className="overflow-hidden rounded-2xl border border-white/15 bg-black/20 shadow-lg">
                <div
                  className="flex aspect-[4/3] items-center justify-center"
                  style={{
                    background: `linear-gradient(135deg, ${theme.gradient[0]}, ${theme.gradient[1] ?? theme.accent})`,
                  }}
                >
                  <ImageIcon className="size-8 opacity-70" strokeWidth={1.5} />
                </div>
                <p className="px-3 py-2 text-left text-[0.65rem] leading-snug opacity-85">
                  Так получатель увидит фото и сообщения в этой теме
                </p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="box"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.94 }}
              className="flex w-full flex-col items-center"
            >
              <GiftBox3D
                palette={giftPalette}
                size="lg"
                opening={phase === "open"}
                isOpen={phase === "reveal"}
              />

              {isIdle ? (
                <motion.button
                  type="button"
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-5 inline-flex size-12 items-center justify-center rounded-full border border-white/20 bg-white/10 text-white shadow-lg backdrop-blur-sm transition hover:scale-105 hover:bg-white/16"
                  style={{
                    boxShadow: `0 12px 28px -14px ${theme.accent}`,
                  }}
                  aria-label="Посмотреть анимацию открытия"
                  onClick={() => void playAnimation()}
                >
                  <Play className="size-5 fill-current" />
                </motion.button>
              ) : (
                <motion.p
                  key="opening"
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="font-display mt-4 text-sm"
                >
                  {phase === "open" || phase === "reveal" ? "Открывается!" : null}
                </motion.p>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
