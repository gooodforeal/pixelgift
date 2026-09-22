import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Home } from "lucide-react";

import { PageTransition } from "../components/PageTransition";

const SPARKS = [
  { x: "12%", y: "18%", size: 4, delay: 0, duration: 3.2 },
  { x: "78%", y: "22%", size: 3, delay: 0.6, duration: 2.8 },
  { x: "22%", y: "72%", size: 3.5, delay: 1.1, duration: 3.6 },
  { x: "86%", y: "68%", size: 2.5, delay: 0.3, duration: 2.4 },
  { x: "48%", y: "12%", size: 2, delay: 1.4, duration: 3 },
  { x: "64%", y: "80%", size: 3, delay: 0.9, duration: 2.6 },
];

function FloatingBalloon() {
  return (
    <motion.div
      className="relative mx-auto h-44 w-36"
      animate={{ y: [0, -14, 0], rotate: [-3, 3, -3] }}
      transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut" }}
    >
      <motion.div
        aria-hidden
        className="absolute left-1/2 top-8 h-28 w-28 -translate-x-1/2 rounded-full bg-rose-500/35 blur-2xl"
        animate={{ opacity: [0.35, 0.6, 0.35], scale: [0.9, 1.08, 0.9] }}
        transition={{ duration: 3.8, repeat: Infinity, ease: "easeInOut" }}
      />
      <svg
        viewBox="0 0 120 170"
        className="relative z-10 h-full w-full drop-shadow-[0_18px_40px_rgba(244,63,94,0.35)]"
        aria-hidden
      >
        <defs>
          <linearGradient id="balloon-body" x1="20%" y1="0%" x2="80%" y2="100%">
            <stop offset="0%" stopColor="#fb7185" />
            <stop offset="45%" stopColor="#e11d48" />
            <stop offset="100%" stopColor="#9f1239" />
          </linearGradient>
          <linearGradient id="balloon-shine" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fff" stopOpacity="0.55" />
            <stop offset="55%" stopColor="#fff" stopOpacity="0" />
          </linearGradient>
        </defs>
        <ellipse cx="60" cy="58" rx="42" ry="50" fill="url(#balloon-body)" />
        <ellipse cx="46" cy="40" rx="12" ry="18" fill="url(#balloon-shine)" />
        <path d="M52 105 L60 114 L68 105 Z" fill="#be123c" />
        <path
          d="M60 114 C58 128 66 140 58 156 C52 168 62 168 60 168"
          fill="none"
          stroke="rgba(226,232,240,0.45)"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </svg>
    </motion.div>
  );
}

export function NotFoundPage() {
  return (
    <PageTransition>
      <div className="relative grid min-h-[70dvh] place-items-center overflow-hidden py-10 text-center">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 -z-10"
        >
          <div className="absolute left-1/2 top-1/3 h-72 w-72 -translate-x-1/2 rounded-full bg-glow-violet/20 blur-[100px]" />
          <div className="absolute bottom-10 left-[15%] h-48 w-48 rounded-full bg-glow-pink/15 blur-[90px]" />
          <div className="absolute right-[12%] top-16 h-40 w-40 rounded-full bg-glow-cyan/10 blur-[80px]" />
          {SPARKS.map((spark) => (
            <motion.span
              key={`${spark.x}-${spark.y}`}
              className="absolute rounded-full bg-white"
              style={{
                left: spark.x,
                top: spark.y,
                width: spark.size,
                height: spark.size,
              }}
              animate={{ opacity: [0.15, 0.85, 0.15], scale: [0.7, 1.2, 0.7] }}
              transition={{
                duration: spark.duration,
                delay: spark.delay,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 22, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="glass relative w-full max-w-md overflow-hidden px-8 py-12 sm:px-10 sm:py-14"
        >
          <div
            aria-hidden
            className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent"
          />

          <FloatingBalloon />

          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.12 }}
            className="font-display mt-2 text-[4.5rem] leading-none tracking-tight text-white/10 sm:text-[5.5rem]"
          >
            404
          </motion.p>

          <motion.h1
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.18 }}
            className="font-display -mt-6 text-3xl tracking-tight sm:text-4xl"
          >
            Страница улетела
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.26 }}
            className="mx-auto mt-3 max-w-xs text-sm leading-relaxed text-slate-400"
          >
            Такой страницы нет — возможно, ссылка устарела или шар унёс её слишком далеко.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.34 }}
            className="mt-8 flex flex-wrap items-center justify-center gap-3"
          >
            <Link to="/" className="btn-primary">
              <Home className="size-4" />
              На главную
            </Link>
            <Link to="/support" className="btn-ghost">
              Поддержка
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </PageTransition>
  );
}
