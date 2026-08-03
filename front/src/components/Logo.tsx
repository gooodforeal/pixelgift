import { Link } from "react-router-dom";

export function Logo({ to = "/" }: { to?: string }) {
  return (
    <Link to={to} className="group flex min-w-0 items-center gap-2 sm:gap-2.5">
      <span className="relative grid size-8 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-glow-pink via-glow-violet to-glow-cyan text-base shadow-lg shadow-glow-violet/30 transition group-hover:scale-105 sm:size-9 sm:rounded-2xl sm:text-lg">
        🎁
      </span>
      <span className="font-display truncate text-base tracking-tight sm:text-lg">
        Pixel<span className="text-gradient">gift</span>
      </span>
    </Link>
  );
}
