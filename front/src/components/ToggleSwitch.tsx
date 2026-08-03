interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  disabled?: boolean;
  className?: string;
}

export function ToggleSwitch({
  checked,
  onChange,
  label,
  disabled = false,
  className = "",
}: ToggleSwitchProps) {
  return (
    <label
      className={`toggle-switch ${checked ? "is-on" : ""} ${disabled ? "is-disabled" : ""} ${className}`}
    >
      <input
        type="checkbox"
        className="sr-only"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange(event.target.checked)}
      />
      <span className="toggle-switch__track" aria-hidden>
        <span className="toggle-switch__thumb" />
      </span>
      <span className="toggle-switch__label">{label}</span>
    </label>
  );
}
