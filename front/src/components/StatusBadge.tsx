import { Archive, CalendarClock, Gift, PencilLine, Sparkles } from "lucide-react";

import { statusLabels } from "../lib/format";
import type { BoxStatus } from "../lib/types";

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
    <span className={`status-badge status-badge--${status}`}>
      <Icon className="status-badge__icon" strokeWidth={2.25} />
      <span>{statusLabels[status]}</span>
    </span>
  );
}
