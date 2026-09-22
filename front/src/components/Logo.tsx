import { useId } from "react";
import { Link } from "react-router-dom";

/** Gift mark for the gradient logo badge — sized to fill most of the circle. */
export function LogoMark({ className = "" }: { className?: string }) {
  const uid = useId().replace(/:/g, "");
  const boxGrad = `${uid}-box`;
  const lidGrad = `${uid}-lid`;
  const ribbonGrad = `${uid}-ribbon`;
  const bowGrad = `${uid}-bow`;

  return (
    <svg
      viewBox="0 0 40 40"
      className={className}
      aria-hidden
      focusable="false"
    >
      <defs>
        <linearGradient id={boxGrad} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="100%" stopColor="#f3e8ff" />
        </linearGradient>
        <linearGradient id={lidGrad} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="100%" stopColor="#fce7f3" />
        </linearGradient>
        <linearGradient id={ribbonGrad} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#fde68a" />
          <stop offset="55%" stopColor="#fbbf24" />
          <stop offset="100%" stopColor="#f59e0b" />
        </linearGradient>
        <linearGradient id={bowGrad} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f9a8d4" />
          <stop offset="50%" stopColor="#f472b6" />
          <stop offset="100%" stopColor="#c084fc" />
        </linearGradient>
      </defs>

      <ellipse cx="20" cy="36" rx="12" ry="1.8" fill="#0b0616" opacity="0.2" />

      {/* Body — larger, fills more of the badge */}
      <rect
        x="7"
        y="16"
        width="26"
        height="17.5"
        rx="2.8"
        fill={`url(#${boxGrad})`}
      />

      {/* Thicker cross ribbon */}
      <rect x="17.6" y="16" width="4.8" height="17.5" fill={`url(#${ribbonGrad})`} />
      <rect x="7" y="22.4" width="26" height="4.2" fill={`url(#${ribbonGrad})`} />

      {/* Lid */}
      <rect
        x="5.5"
        y="12.2"
        width="29"
        height="5.2"
        rx="2"
        fill={`url(#${lidGrad})`}
      />
      <rect x="17.6" y="12.2" width="4.8" height="5.2" fill={`url(#${ribbonGrad})`} />

      {/* Bow */}
      <path
        d="M20 11.2
           C16.8 11.2 13.4 10.2 11.6 8.2
           C10 6.4 10.7 4.4 13 4.6
           C15.8 4.9 18.2 7 20 9.4
           Z"
        fill={`url(#${bowGrad})`}
      />
      <path
        d="M20 11.2
           C23.2 11.2 26.6 10.2 28.4 8.2
           C30 6.4 29.3 4.4 27 4.6
           C24.2 4.9 21.8 7 20 9.4
           Z"
        fill={`url(#${bowGrad})`}
      />
      <rect
        x="17.4"
        y="9.4"
        width="5.2"
        height="3.6"
        rx="1.2"
        fill={`url(#${ribbonGrad})`}
      />
      <circle cx="20" cy="11.2" r="1.35" fill="#22d3ee" />

      <path
        d="M18.2 12.4 C16.4 14.2 15.4 15.8 15.9 16.3 C16.6 15.2 18.1 13.8 19 12.8 Z"
        fill={`url(#${bowGrad})`}
        opacity="0.9"
      />
      <path
        d="M21.8 12.4 C23.6 14.2 24.6 15.8 24.1 16.3 C23.4 15.2 21.9 13.8 21 12.8 Z"
        fill={`url(#${bowGrad})`}
        opacity="0.9"
      />
    </svg>
  );
}

export function Logo({ to = "/" }: { to?: string }) {
  return (
    <Link to={to} className="group flex min-w-0 items-center gap-2 sm:gap-2.5">
      <span className="relative grid size-8 shrink-0 place-items-center overflow-hidden rounded-xl bg-gradient-to-br from-glow-pink via-glow-violet to-glow-cyan shadow-lg shadow-glow-violet/30 transition group-hover:scale-105 sm:size-9 sm:rounded-2xl">
        <LogoMark className="size-[1.7rem] sm:size-[1.9rem]" />
      </span>
      <span className="font-display truncate text-base tracking-tight sm:text-lg">
        Pixel<span className="text-gradient">gift</span>
      </span>
    </Link>
  );
}
