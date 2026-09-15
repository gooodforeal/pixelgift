import { Archive, CalendarClock, Gift, PencilLine, Sparkles } from "lucide-react";

import { statusLabels } from "../lib/format";
import type { BoxStatus } from "../lib/types";

const styles: Record<BoxStatus, string> = {
  draft:
    "status-badge status-badge--draft border-slate-300/40 bg-slate-950/80 text-slate-100",
  scheduled:
    "status-badge status-badge--scheduled border-violet-300/45 bg-violet-950/85 text-violet-100",
  active:
    "status-badge status-badge--active border-cyan-300/45 bg-cyan-950/85 text-cyan-100",
  opened:
    "status-badge status-badge--opened border-emerald-300/45 bg-emerald-950/85 text-emerald-100",
  archived:
    "status-badge status-badge--archived border-white/25 bg-ink-950/85 text-slate-100",
};

const icons: Record<BoxStatus, typeof PencilLine> = {
  draft: PencilLine,
  scheduled: CalendarClock,
  active: Gift,
  opened: Sparkles,
  archived: Archive,
};

export function StatusBadge({ status }: { status: BoxStatus }) {
  const Icon = icons[status];

  return (
    <span
      className={`status-badge inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold shadow-lg shadow-black/35 backdrop-blur-md ${styles[status]}`}
    >
      <Icon className="size-3.5" />
      {statusLabels[status]}
    </span>
  );
}
