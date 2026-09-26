/** Avatar for Gifti — the PixelGift box-editor assistant. */
export function GiftiAvatar({
  className = "size-9",
  title = "Гифти",
}: {
  className?: string;
  title?: string;
}) {
  return (
    <svg
      className={className}
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label={title}
    >
      <title>{title}</title>
      {/* Inset from viewBox edges so stroke is not clipped at small sizes */}
      <circle cx="20" cy="20" r="18.25" className="fill-cyan-400/25" />
      <circle
        cx="20"
        cy="20"
        r="18.25"
        className="stroke-cyan-300/50"
        strokeWidth="1.25"
        fill="none"
      />
      {/* gift box */}
      <rect
        x="11"
        y="16"
        width="18"
        height="14"
        rx="2.5"
        className="fill-cyan-300/90"
      />
      <rect
        x="10.5"
        y="13"
        width="19"
        height="5"
        rx="1.5"
        className="fill-fuchsia-300/85"
      />
      {/* ribbon */}
      <rect x="18.5" y="13" width="3" height="17" className="fill-fuchsia-500/90" />
      {/* bow */}
      <path
        d="M20 11.5C17.2 8.4 13.8 9.6 14.2 12.2C14.5 13.8 17.2 14.2 20 12.6C22.8 14.2 25.5 13.8 25.8 12.2C26.2 9.6 22.8 8.4 20 11.5Z"
        className="fill-fuchsia-400"
      />
      <circle cx="20" cy="12.2" r="1.4" className="fill-fuchsia-200" />
      {/* sparkle eyes */}
      <circle cx="15.5" cy="22.5" r="1.2" className="fill-slate-900/70" />
      <circle cx="24.5" cy="22.5" r="1.2" className="fill-slate-900/70" />
      <path
        d="M17.2 26.2C18 27.1 19 27.5 20 27.5C21 27.5 22 27.1 22.8 26.2"
        className="stroke-slate-900/55"
        strokeWidth="1.2"
        strokeLinecap="round"
        fill="none"
      />
    </svg>
  );
}
