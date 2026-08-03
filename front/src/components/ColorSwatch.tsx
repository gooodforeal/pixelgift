interface ColorSwatchProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

export function ColorSwatch({ label, value, onChange }: ColorSwatchProps) {
  return (
    <label className="color-swatch">
      <span className="color-swatch__control">
        <span className="color-swatch__ring" style={{ background: value }} aria-hidden>
          <span className="color-swatch__disc" style={{ background: value }} />
        </span>
        <input
          type="color"
          className="color-swatch__input"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          aria-label={label}
        />
      </span>
      <span className="color-swatch__meta">
        <span className="color-swatch__label">{label}</span>
        <span className="color-swatch__hex">{value.toUpperCase()}</span>
      </span>
    </label>
  );
}
