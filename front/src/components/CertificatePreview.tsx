export type CertificateTheme = "dark" | "light";

const MOCK = {
  title: "День рождения",
  recipientName: "Алиса",
  activatesAt: "19 сентября 2026 г. в 18:00",
  password: "gift2026",
  giftUrl: "https://pixelgift.app/b/demo",
} as const;

interface CertificatePreviewProps {
  theme: CertificateTheme;
}

/** Compact A4-ratio mock of the printable certificate (not live box data). */
export function CertificatePreview({ theme }: CertificatePreviewProps) {
  const dark = theme === "dark";

  return (
    <div className="flex justify-center">
      <div
        className={`certificate-preview relative w-[min(100%,13.5rem)] overflow-hidden rounded-xl border shadow-lg sm:aspect-[210/297] sm:w-[15rem] ${
          dark
            ? "border-glow-pink/40 bg-[#0b0718] text-white shadow-black/40"
            : "border-glow-violet/30 bg-[#f7f4ff] text-ink-900 shadow-slate-900/10"
        }`}
      >
        <div
          className={`pointer-events-none absolute -top-8 -left-6 size-24 rounded-full blur-2xl ${
            dark ? "bg-glow-violet/30" : "bg-glow-violet/20"
          }`}
        />
        <div
          className={`pointer-events-none absolute -right-4 -bottom-6 size-20 rounded-full blur-2xl ${
            dark ? "bg-glow-pink/25" : "bg-glow-pink/20"
          }`}
        />

        <div
          className={`relative flex h-full min-h-0 flex-col px-3 py-3 ${
            dark
              ? "m-1.5 rounded-lg border border-glow-violet/30"
              : "m-1.5 rounded-lg border border-glow-violet/20 bg-white/40"
          }`}
        >
          <p className="font-display text-center text-[0.9rem] leading-none tracking-tight">
            Pixel<span className="text-gradient">gift</span>
          </p>
          <p
            className={`mt-1 text-center text-[0.5rem] leading-tight ${
              dark ? "text-slate-400" : "text-slate-500"
            }`}
          >
            Сертификат на цифровой подарок
          </p>
          <div className="mx-auto mt-1 h-px w-8 bg-glow-gold/80" />

          <p
            className={`mt-2 text-center text-[0.6rem] font-semibold leading-snug ${
              dark ? "text-slate-100" : "text-ink-900"
            }`}
          >
            {MOCK.title}
          </p>

          <div
            className={`mt-2 rounded-lg px-2 py-1.5 ${
              dark ? "bg-ink-700/80" : "border border-violet-100 bg-white"
            }`}
          >
            <p
              className={`text-[0.45rem] font-semibold tracking-wider uppercase ${
                dark ? "text-slate-500" : "text-slate-400"
              }`}
            >
              Для
            </p>
            <p className="text-[0.65rem] font-semibold leading-tight">
              {MOCK.recipientName}
            </p>
            <p
              className={`mt-1 text-[0.45rem] font-semibold tracking-wider uppercase ${
                dark ? "text-slate-500" : "text-slate-400"
              }`}
            >
              Откроется
            </p>
            <p
              className={`text-[0.5rem] leading-tight ${
                dark ? "text-glow-cyan" : "text-cyan-700"
              }`}
            >
              {MOCK.activatesAt}
            </p>
          </div>

          <div
            className={`mt-1.5 rounded-lg border px-2 py-1.5 text-center ${
              dark
                ? "border-glow-gold/50 bg-ink-800/90"
                : "border-amber-300/70 bg-amber-50"
            }`}
          >
            <p
              className={`text-[0.45rem] font-semibold tracking-wider uppercase ${
                dark ? "text-glow-gold" : "text-amber-700"
              }`}
            >
              Пароль для открытия
            </p>
            <p className="mt-0.5 font-display text-[0.75rem] tracking-widest">
              {MOCK.password}
            </p>
          </div>

          <div className="mt-auto flex flex-col items-center gap-0.5 pt-2 pb-0.5">
            <div
              className={`grid size-12 place-items-center rounded-md border bg-white ${
                dark ? "border-white/10" : "border-slate-200"
              }`}
            >
              <QrPlaceholder seed={MOCK.giftUrl} />
            </div>
            <p
              className={`text-center text-[0.45rem] leading-tight ${
                dark ? "text-slate-400" : "text-slate-500"
              }`}
            >
              Отсканируй QR — страница подарка
            </p>
            <p
              className={`max-w-full truncate px-1 text-center font-mono text-[0.4rem] ${
                dark ? "text-glow-cyan/80" : "text-cyan-700"
              }`}
            >
              {MOCK.giftUrl}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function QrPlaceholder({ seed }: { seed: string }) {
  const cells = 9;
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return (
    <div
      className="grid gap-px"
      style={{
        gridTemplateColumns: `repeat(${cells}, minmax(0, 1fr))`,
        width: "2.25rem",
        height: "2.25rem",
      }}
      aria-hidden
    >
      {Array.from({ length: cells * cells }, (_, index) => {
        const on = ((hash + index * 17) % 5) > 1;
        const edge =
          index % cells < 2 ||
          index % cells >= cells - 2 ||
          index < cells * 2 ||
          index >= cells * (cells - 2);
        return (
          <span
            key={index}
            className={on || edge ? "bg-ink-900" : "bg-transparent"}
          />
        );
      })}
    </div>
  );
}
