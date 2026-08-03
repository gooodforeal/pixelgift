import { useEffect, useState } from "react";

import { countdownTo, type Countdown } from "../lib/format";

export function useCountdown(iso: string, onFinish?: () => void): Countdown {
  const [value, setValue] = useState(() => countdownTo(iso));

  useEffect(() => {
    setValue(countdownTo(iso));
    if (new Date(iso).getTime() <= Date.now()) return;

    const timer = window.setInterval(() => {
      const next = countdownTo(iso);
      setValue(next);
      if (next.totalMs === 0) {
        window.clearInterval(timer);
        onFinish?.();
      }
    }, 1000);

    return () => window.clearInterval(timer);
  }, [iso, onFinish]);

  return value;
}
