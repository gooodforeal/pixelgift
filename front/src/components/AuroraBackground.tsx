interface AuroraBackgroundProps {
  colors?: [string, string, string];
}

export function AuroraBackground({
  colors = ["#a855f7", "#22d3ee", "#f472b6"],
}: AuroraBackgroundProps) {
  return (
    <div
      aria-hidden
      className="aurora-layer pointer-events-none fixed inset-0 -z-10 overflow-hidden"
    >
      <div
        className="aurora-blob absolute -top-40 -left-32 h-[34rem] w-[34rem] rounded-full opacity-30 blur-[120px]"
        style={{ background: colors[0] }}
      />
      <div
        className="aurora-blob absolute top-1/4 -right-40 h-[30rem] w-[30rem] rounded-full opacity-22 blur-[130px]"
        style={{ background: colors[1] }}
      />
      <div
        className="aurora-blob absolute -bottom-52 left-1/3 h-[32rem] w-[32rem] rounded-full opacity-20 blur-[140px]"
        style={{ background: colors[2] }}
      />
    </div>
  );
}
