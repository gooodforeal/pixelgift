import type { BoxStatus } from "./types";

export const localTimezone =
  Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";

const dateTimeFormatter = new Intl.DateTimeFormat("ru-RU", {
  day: "numeric",
  month: "long",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

export function formatDateTime(iso: string): string {
  return dateTimeFormatter.format(new Date(iso));
}

/** ISO string → value for <input type="datetime-local"> in local time. */
export function toDateTimeLocal(iso: string): string {
  const date = new Date(iso);
  const offset = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

/** Split local datetime-local value ("YYYY-MM-DDTHH:mm") into date + time. */
export function splitDateTimeLocal(value: string): { date: string; time: string } {
  if (!value) return { date: "", time: "" };
  const [date = "", time = ""] = value.split("T");
  return { date, time: time.slice(0, 5) };
}

export function joinDateTimeLocal(date: string, time: string): string {
  if (!date) return "";
  return `${date}T${time || "00:00"}`;
}

export function fromDateTimeLocal(value: string): string {
  return new Date(value).toISOString();
}

export function defaultActivatesAt(): string {
  const date = new Date();
  date.setSeconds(0, 0);
  date.setMinutes(date.getMinutes() + 1);
  return toDateTimeLocal(date.toISOString());
}

export interface Countdown {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  totalMs: number;
}

export function countdownTo(iso: string, now: number = Date.now()): Countdown {
  const totalMs = Math.max(0, new Date(iso).getTime() - now);
  const totalSeconds = Math.floor(totalMs / 1000);
  return {
    days: Math.floor(totalSeconds / 86_400),
    hours: Math.floor((totalSeconds % 86_400) / 3_600),
    minutes: Math.floor((totalSeconds % 3_600) / 60),
    seconds: totalSeconds % 60,
    totalMs,
  };
}

export const statusLabels: Record<BoxStatus, string> = {
  draft: "Черновик",
  scheduled: "Запланирован",
  active: "Можно открыть",
  opened: "Открыт",
  archived: "В архиве",
};

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} КБ`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
}

export function pluralize(count: number, forms: [string, string, string]): string {
  const mod10 = count % 10;
  const mod100 = count % 100;
  if (mod10 === 1 && mod100 !== 11) return forms[0];
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return forms[1];
  return forms[2];
}
