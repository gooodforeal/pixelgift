type TelegramIconProps = {
  className?: string;
};

/** Логотип Telegram (официальный контур «бумажный самолётик»). */
export function TelegramIcon({ className = "size-4" }: TelegramIconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden
    >
      <path d="M9.417 15.181l-.397 5.584c.568 0 .814-.244 1.109-.537l2.663-2.599 5.523 4.037c1.012.564 1.725.267 1.998-.931L23.93 3.821c.321-1.496-.541-2.081-1.527-1.67L2.114 9.815c-1.496.581-1.473 1.413-.27 1.79l5.452 1.706L18.237 5.87c.622-.415 1.185-.186.721.231L9.417 15.18z" />
    </svg>
  );
}
