import { ChevronRight } from "lucide-react";

export type BoxWizardStepId =
  | "design"
  | "details"
  | "content"
  | "publish"
  | "certificate";

export interface BoxWizardStep {
  id: BoxWizardStepId;
  title: string;
  instruction: string;
}

export const BOX_WIZARD_STEPS: BoxWizardStep[] = [
  {
    id: "design",
    title: "Оформление",
    instruction:
      "Выберите тему — она задаёт фон, частицы и анимацию открытия бокса.",
  },
  {
    id: "details",
    title: "Детали",
    instruction:
      "Заполните название, получателя, дату открытия и письмо внутри бокса.",
  },
  {
    id: "content",
    title: "Содержимое",
    instruction:
      "Добавьте фото, видео, голосовые или текст — до 12 карточек в одном боксе.",
  },
  {
    id: "publish",
    title: "Публикация",
    instruction: "Проверьте ссылку и опубликуйте бокс, когда будете готовы.",
  },
  {
    id: "certificate",
    title: "Сертификат",
    instruction:
      "Скачайте PDF-сертификат с QR и паролем — после публикации бокса.",
  },
];

interface BoxWizardProgressProps {
  current: BoxWizardStepId;
  /** Highest step index the user may jump to (inclusive). */
  maxReachableIndex: number;
  onSelect: (stepId: BoxWizardStepId) => void;
}

export function BoxWizardProgress({
  current,
  maxReachableIndex,
  onSelect,
}: BoxWizardProgressProps) {
  const currentIndex = BOX_WIZARD_STEPS.findIndex((step) => step.id === current);
  const active = BOX_WIZARD_STEPS[currentIndex] ?? BOX_WIZARD_STEPS[0];
  const progress =
    BOX_WIZARD_STEPS.length <= 1
      ? 100
      : (currentIndex / (BOX_WIZARD_STEPS.length - 1)) * 100;

  return (
    <div className="box-wizard">
      <div className="box-wizard__track" aria-hidden>
        <div className="box-wizard__bar" style={{ width: `${progress}%` }} />
      </div>

      <ol className="box-wizard__steps">
        {BOX_WIZARD_STEPS.map((step, index) => {
          const reachable = index <= maxReachableIndex;
          const done = index < currentIndex;
          const isCurrent = index === currentIndex;
          const showArrow = index < BOX_WIZARD_STEPS.length - 1;

          return (
            <li key={step.id} className="box-wizard__step-wrap">
              <button
                type="button"
                className={`box-wizard__step ${done ? "is-done" : ""} ${
                  isCurrent ? "is-current" : ""
                } ${reachable ? "" : "is-locked"}`}
                disabled={!reachable}
                aria-current={isCurrent ? "step" : undefined}
                onClick={() => {
                  if (reachable) onSelect(step.id);
                }}
              >
                <span className="box-wizard__num">{index + 1}</span>
                <span className="box-wizard__label">{step.title}</span>
              </button>
              {showArrow ? (
                <ChevronRight
                  className="box-wizard__arrow"
                  aria-hidden
                  strokeWidth={2}
                />
              ) : null}
            </li>
          );
        })}
      </ol>

      <div className="box-wizard__hint">
        <p className="box-wizard__hint-kicker">
          Шаг {currentIndex + 1} из {BOX_WIZARD_STEPS.length}
        </p>
        <h2 className="box-wizard__hint-title">{active.title}</h2>
        <p className="box-wizard__hint-text">{active.instruction}</p>
      </div>
    </div>
  );
}

export function isBoxWizardStepId(value: string | null): value is BoxWizardStepId {
  return BOX_WIZARD_STEPS.some((step) => step.id === value);
}
