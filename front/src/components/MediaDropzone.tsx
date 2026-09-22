import { useRef, useState } from "react";
import {
  Brush,
  CircleHelp,
  CirclePlay,
  Film,
  Gift,
  ImagePlus,
  Loader2,
  MapPin,
  Mic,
  Plus,
  Sparkles,
  Trash2,
  Type,
  type LucideIcon,
} from "lucide-react";

import { CircleRecorder } from "./CircleRecorder";
import { DrawingCanvas } from "./DrawingCanvas";
import { MapPointPicker } from "./MapPointPicker";
import { ToggleSwitch } from "./ToggleSwitch";
import {
  filterFilesByMediaKind,
  getMediaKindOption,
  MEDIA_KIND_OPTIONS,
} from "../lib/mediaKinds";
import {
  DEFAULT_GEOPOINT,
  formatGeopointCoords,
  type GeopointCoords,
} from "../lib/geopoint";
import { MAX_BOX_ITEM_CAPTION } from "../lib/limits";
import {
  emptyQuestionDraft,
  QUESTION_OPTION_MAX,
  QUESTION_OPTIONS_MAX,
  QUESTION_OPTIONS_MIN,
  QUESTION_TEXT_MAX,
  QUESTION_TEXT_MIN,
} from "../lib/question";
import { isSecretPhotoType } from "../lib/secret";
import { TOY_OPTIONS, toyImageUrl } from "../lib/toys";
import type { BoxItemType } from "../lib/types";

const ICONS: Record<BoxItemType, LucideIcon> = {
  image: ImagePlus,
  drawing: Brush,
  gif: Sparkles,
  video: Film,
  circle: CirclePlay,
  voice: Mic,
  text: Type,
  toy: Gift,
  geopoint: MapPin,
  question: CircleHelp,
};

interface MediaDropzoneProps {
  kind: BoxItemType;
  onKindChange: (kind: BoxItemType) => void;
  onFiles: (files: File[]) => void;
  onAddText?: (text: string) => void;
  onAddDrawing?: (blob: Blob) => void;
  onAddCircle?: (blob: Blob) => void;
  onAddToy?: (toyCode: string, caption: string) => void;
  onAddGeopoint?: (coords: GeopointCoords, caption: string) => void;
  onAddQuestion?: (payload: {
    question: string;
    options: string[];
    correct_index: number;
  }) => void;
  onRejected?: (files: File[], kind: BoxItemType) => void;
  secretPhoto?: boolean;
  onSecretPhotoChange?: (secret: boolean) => void;
  uploading: boolean;
  disabled?: boolean;
}

export function MediaDropzone({
  kind,
  onKindChange,
  onFiles,
  onAddText,
  onAddDrawing,
  onAddCircle,
  onAddToy,
  onAddGeopoint,
  onAddQuestion,
  onRejected,
  secretPhoto = false,
  onSecretPhotoChange,
  uploading,
  disabled = false,
}: MediaDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [textDraft, setTextDraft] = useState("");
  const [toyCode, setToyCode] = useState(TOY_OPTIONS[0]?.code ?? "bear");
  const [toyCaption, setToyCaption] = useState("");
  const [geoCoords, setGeoCoords] = useState<GeopointCoords | null>(
    DEFAULT_GEOPOINT,
  );
  const [geoCaption, setGeoCaption] = useState("");
  const [questionDraft, setQuestionDraft] = useState(emptyQuestionDraft);
  const option = getMediaKindOption(kind);
  const Icon = ICONS[kind];
  const isText = Boolean(option.isText);
  const isDrawing = kind === "drawing";
  const isCircle = kind === "circle";
  const isToy = Boolean(option.isToy);
  const isGeopoint = Boolean(option.isGeopoint);
  const isQuestion = Boolean(option.isQuestion);

  const handleFiles = (fileList: FileList | null) => {
    if (
      !fileList ||
      disabled ||
      isText ||
      isDrawing ||
      isCircle ||
      isToy ||
      isGeopoint ||
      isQuestion
    )
      return;
    const { accepted, rejected } = filterFilesByMediaKind(
      Array.from(fileList),
      kind,
    );
    if (rejected.length > 0) onRejected?.(rejected, kind);
    if (accepted.length > 0) onFiles(accepted);
  };

  const submitText = () => {
    const value = textDraft.trim();
    if (!value || disabled || uploading) return;
    onAddText?.(value);
    setTextDraft("");
  };

  const submitToy = () => {
    if (!toyCode || disabled || uploading) return;
    onAddToy?.(toyCode, toyCaption.trim());
    setToyCaption("");
  };

  const submitGeopoint = () => {
    if (!geoCoords || disabled || uploading) return;
    onAddGeopoint?.(geoCoords, geoCaption.trim());
    setGeoCaption("");
  };

  const questionOptionsFilled = questionDraft.options.map((o) => o.trim());
  const questionReady =
    questionDraft.question.trim().length >= QUESTION_TEXT_MIN &&
    questionDraft.question.trim().length <= QUESTION_TEXT_MAX &&
    questionOptionsFilled.length >= QUESTION_OPTIONS_MIN &&
    questionOptionsFilled.every(
      (text) => text.length > 0 && text.length <= QUESTION_OPTION_MAX,
    ) &&
    questionDraft.correctIndex >= 0 &&
    questionDraft.correctIndex < questionOptionsFilled.length;

  const submitQuestion = () => {
    if (!questionReady || disabled || uploading) return;
    onAddQuestion?.({
      question: questionDraft.question.trim(),
      options: questionOptionsFilled,
      correct_index: questionDraft.correctIndex,
    });
    setQuestionDraft(emptyQuestionDraft());
  };

  return (
    <div className="space-y-4">
      <div>
        <p className="label">Тип карточки</p>
        <div
          role="tablist"
          aria-label="Тип карточки"
          className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4"
        >
          {MEDIA_KIND_OPTIONS.map((item) => {
            const ItemIcon = ICONS[item.kind];
            const selected = item.kind === kind;
            return (
              <button
                key={item.kind}
                type="button"
                role="tab"
                aria-selected={selected}
                disabled={disabled || uploading}
                onClick={() => onKindChange(item.kind)}
                className={`media-kind-btn flex min-w-0 items-center gap-2.5 rounded-2xl border px-3.5 py-3 text-left transition ${
                  selected
                    ? "is-selected border-glow-violet/50 bg-glow-violet/15 text-slate-100"
                    : "border-white/10 bg-white/[0.03] text-slate-400 hover:border-white/20 hover:text-slate-200"
                } disabled:opacity-50`}
              >
                <span
                  className={`grid size-8 shrink-0 place-items-center rounded-xl ${
                    selected
                      ? "bg-glow-violet/25 text-glow-violet"
                      : "bg-white/5 text-current"
                  }`}
                >
                  <ItemIcon className="size-4" />
                </span>
                <span className="min-w-0">
                  <span className="block truncate text-sm font-semibold leading-tight">
                    {item.label}
                  </span>
                  <span className="mt-0.5 block truncate text-[0.65rem] leading-snug opacity-65">
                    {item.shortHint}
                  </span>
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {isText ? (
        <div className="space-y-3 rounded-3xl border border-white/12 bg-white/[0.02] p-4 sm:p-5">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-100">
            <Type className="size-4 text-glow-violet" />
            Текстовая карточка
          </div>
          <textarea
            className="field min-h-28 resize-y"
            placeholder="Напишите сообщение, которое увидит получатель…"
            value={textDraft}
            disabled={disabled || uploading}
            maxLength={MAX_BOX_ITEM_CAPTION}
            onChange={(event) => setTextDraft(event.target.value)}
          />
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-slate-400">
              До {MAX_BOX_ITEM_CAPTION} символов · без файла
            </p>
            <button
              type="button"
              className="btn-primary px-5 py-2.5 text-sm"
              disabled={disabled || uploading || !textDraft.trim()}
              onClick={submitText}
            >
              {uploading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Добавляем…
                </>
              ) : (
                "Добавить текст"
              )}
            </button>
          </div>
        </div>
      ) : isDrawing ? (
        <DrawingCanvas
          disabled={disabled}
          uploading={uploading}
          onSubmit={(blob) => onAddDrawing?.(blob)}
        />
      ) : isCircle ? (
        <CircleRecorder
          disabled={disabled}
          uploading={uploading}
          onSubmit={(blob) => onAddCircle?.(blob)}
        />
      ) : isToy ? (
        <div className="space-y-4 rounded-3xl border border-white/12 bg-white/[0.02] p-4 sm:p-5">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-100">
            <Gift className="size-4 text-glow-violet" />
            Плюшевая игрушка
          </div>
          <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3">
            {TOY_OPTIONS.map((toy) => {
              const selected = toy.code === toyCode;
              return (
                <button
                  key={toy.code}
                  type="button"
                  disabled={disabled || uploading}
                  onClick={() => setToyCode(toy.code)}
                  className={`flex h-full flex-col overflow-hidden rounded-2xl border text-left transition ${
                    selected
                      ? "border-glow-violet/60 bg-glow-violet/10 shadow-[inset_0_0_0_1px_rgb(168_85_247_/_0.35)]"
                      : "border-white/10 hover:border-white/25"
                  } disabled:opacity-50`}
                >
                  <span className="relative block aspect-square w-full shrink-0 overflow-hidden bg-ink-900">
                    <img
                      src={toyImageUrl(toy.code)}
                      alt={toy.name}
                      className="absolute inset-0 block h-full w-full object-cover object-center"
                      loading="lazy"
                    />
                  </span>
                  <span className="flex min-h-[4.25rem] flex-1 flex-col gap-0.5 px-2.5 py-2">
                    <span className="block text-xs font-semibold text-slate-100">
                      {toy.name}
                    </span>
                    <span className="line-clamp-2 block text-[0.65rem] leading-snug text-slate-400">
                      {toy.description}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
          <div>
            <label className="label" htmlFor="toy-caption">
              Подпись к игрушке
            </label>
            <input
              id="toy-caption"
              className="field"
              placeholder="Этот мишка — для тебя…"
              value={toyCaption}
              disabled={disabled || uploading}
              maxLength={MAX_BOX_ITEM_CAPTION}
              onChange={(event) => setToyCaption(event.target.value)}
            />
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-slate-400">
              Выберите игрушку и добавьте тёплую подпись
            </p>
            <button
              type="button"
              className="btn-primary px-5 py-2.5 text-sm"
              disabled={disabled || uploading || !toyCode}
              onClick={submitToy}
            >
              {uploading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Добавляем…
                </>
              ) : (
                "Добавить игрушку"
              )}
            </button>
          </div>
        </div>
      ) : isGeopoint ? (
        <div className="space-y-4 rounded-3xl border border-white/12 bg-white/[0.02] p-4 sm:p-5">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-100">
            <MapPin className="size-4 text-glow-violet" />
            Точка на карте
          </div>
          <MapPointPicker
            value={geoCoords}
            onChange={setGeoCoords}
            disabled={disabled || uploading}
          />
          <p className="text-xs text-slate-400">
            Нажмите на карту или перетащите маркер
            {geoCoords ? ` · ${formatGeopointCoords(geoCoords)}` : ""}
          </p>
          <div>
            <label className="label" htmlFor="geo-caption">
              Подпись
            </label>
            <input
              id="geo-caption"
              className="field"
              placeholder="Помнишь это место?"
              value={geoCaption}
              disabled={disabled || uploading}
              maxLength={MAX_BOX_ITEM_CAPTION}
              onChange={(event) => setGeoCaption(event.target.value)}
            />
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-slate-400">
              Получатель увидит точку на карте
            </p>
            <button
              type="button"
              className="btn-primary px-5 py-2.5 text-sm"
              disabled={disabled || uploading || !geoCoords}
              onClick={submitGeopoint}
            >
              {uploading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Добавляем…
                </>
              ) : (
                "Добавить точку"
              )}
            </button>
          </div>
        </div>
      ) : isQuestion ? (
        <div className="space-y-4 rounded-3xl border border-white/12 bg-white/[0.02] p-4 sm:p-5">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-100">
            <CircleHelp className="size-4 text-glow-violet" />
            Вопрос с вариантами
          </div>
          <div>
            <label className="label" htmlFor="question-text">
              Вопрос
            </label>
            <input
              id="question-text"
              className="field"
              placeholder="Где мы встретились?"
              value={questionDraft.question}
              disabled={disabled || uploading}
              maxLength={QUESTION_TEXT_MAX}
              onChange={(event) =>
                setQuestionDraft((current) => ({
                  ...current,
                  question: event.target.value,
                }))
              }
            />
            <p className="mt-1.5 text-xs text-slate-500">
              {questionDraft.question.trim().length}/{QUESTION_TEXT_MAX} · от{" "}
              {QUESTION_TEXT_MIN} символов
            </p>
          </div>
          <div className="space-y-2.5">
            <p className="label mb-0">Варианты ответа</p>
            {questionDraft.options.map((optionText, index) => (
              <div key={index} className="flex items-center gap-2">
                <button
                  type="button"
                  className={`grid size-9 shrink-0 place-items-center rounded-full border text-xs font-bold transition ${
                    questionDraft.correctIndex === index
                      ? "border-emerald-400/60 bg-emerald-400/20 text-emerald-200"
                      : "border-white/15 bg-white/5 text-slate-400 hover:border-white/30"
                  }`}
                  title="Отметить правильным"
                  disabled={disabled || uploading}
                  onClick={() =>
                    setQuestionDraft((current) => ({
                      ...current,
                      correctIndex: index,
                    }))
                  }
                >
                  {index + 1}
                </button>
                <input
                  className="field flex-1 py-2.5!"
                  placeholder={`Вариант ${index + 1}`}
                  value={optionText}
                  disabled={disabled || uploading}
                  maxLength={QUESTION_OPTION_MAX}
                  onChange={(event) =>
                    setQuestionDraft((current) => {
                      const options = [...current.options];
                      options[index] = event.target.value;
                      return { ...current, options };
                    })
                  }
                />
                {questionDraft.options.length > QUESTION_OPTIONS_MIN ? (
                  <button
                    type="button"
                    className="btn-ghost grid size-9 shrink-0 place-items-center p-0"
                    disabled={disabled || uploading}
                    aria-label={`Удалить вариант ${index + 1}`}
                    onClick={() =>
                      setQuestionDraft((current) => {
                        const options = current.options.filter(
                          (_, i) => i !== index,
                        );
                        let correctIndex = current.correctIndex;
                        if (index === current.correctIndex) correctIndex = 0;
                        else if (index < current.correctIndex) {
                          correctIndex = Math.max(0, correctIndex - 1);
                        }
                        return { question: current.question, options, correctIndex };
                      })
                    }
                  >
                    <Trash2 className="size-3.5" />
                  </button>
                ) : (
                  <span className="size-9 shrink-0" />
                )}
              </div>
            ))}
            {questionDraft.options.length < QUESTION_OPTIONS_MAX ? (
              <button
                type="button"
                className="btn-ghost inline-flex items-center gap-1.5 px-3 py-2 text-xs"
                disabled={disabled || uploading}
                onClick={() =>
                  setQuestionDraft((current) => ({
                    ...current,
                    options: [...current.options, ""],
                  }))
                }
              >
                <Plus className="size-3.5" />
                Ещё вариант
              </button>
            ) : null}
            <p className="text-xs text-slate-500">
              Нажмите номер слева, чтобы отметить правильный ответ · от{" "}
              {QUESTION_OPTIONS_MIN} до {QUESTION_OPTIONS_MAX} вариантов
            </p>
          </div>
          <div className="mt-2 flex flex-wrap items-center justify-between gap-3 border-t border-white/8 pt-5">
            <p className="text-xs text-slate-400">
              Правильный: вариант {questionDraft.correctIndex + 1}
            </p>
            <button
              type="button"
              className="btn-primary px-5 py-2.5 text-sm"
              disabled={disabled || uploading || !questionReady}
              onClick={submitQuestion}
            >
              {uploading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Добавляем…
                </>
              ) : (
                "Добавить вопрос"
              )}
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {isSecretPhotoType(kind) && onSecretPhotoChange ? (
            <div className="rounded-2xl border border-white/12 bg-white/[0.02] px-4 py-3">
              <ToggleSwitch
                checked={secretPhoto}
                disabled={disabled || uploading}
                label="Секретное фото"
                onChange={onSecretPhotoChange}
              />
              <p className="mt-1.5 text-[0.7rem] leading-snug text-slate-500">
                Получатель сотрёт верхний слой ластиком, чтобы увидеть снимок
              </p>
            </div>
          ) : null}
          <div
            onDragOver={(event) => {
              event.preventDefault();
              if (!disabled) setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(event) => {
              event.preventDefault();
              setDragging(false);
              handleFiles(event.dataTransfer.files);
            }}
            onClick={() => !disabled && inputRef.current?.click()}
            className={`media-dropzone flex cursor-pointer flex-col items-center justify-center gap-3 rounded-3xl border-2 border-dashed px-6 py-10 text-center transition ${
              dragging
                ? "is-dragging border-glow-violet/70 bg-glow-violet/10"
                : "border-white/12 bg-white/[0.02] hover:border-white/25 hover:bg-white/[0.05]"
            } ${disabled ? "pointer-events-none opacity-50" : ""}`}
          >
            <input
              ref={inputRef}
              type="file"
              multiple
              accept={option.accept}
              className="hidden"
              onChange={(event) => {
                handleFiles(event.target.files);
                event.target.value = "";
              }}
            />
            <span className="grid size-12 place-items-center rounded-2xl bg-glow-violet/15 text-glow-violet">
              {uploading ? (
                <Loader2 className="size-6 animate-spin" />
              ) : (
                <Icon className="size-6" />
              )}
            </span>
            <div>
              <div className="text-sm font-semibold text-slate-100">
                {uploading
                  ? `Загружаем ${option.label.toLowerCase()}…`
                  : `Добавить: ${option.label.toLowerCase()}`}
              </div>
              <p className="mt-1 text-xs text-slate-400">
                {option.hint} — до 10 файлов за раз
                {isSecretPhotoType(kind) && secretPhoto
                  ? " · секретный режим"
                  : ""}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
