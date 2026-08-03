interface SpinnerProps {
  label?: string;
  className?: string;
}

export function Spinner({ label, className = "" }: SpinnerProps) {
  return (
    <div className={`flex items-center justify-center gap-3 text-sm text-slate-400 ${className}`}>
      <span className="spinner-ring size-5 animate-spin rounded-full border-2 border-white/15 border-t-glow-violet" />
      {label}
    </div>
  );
}
