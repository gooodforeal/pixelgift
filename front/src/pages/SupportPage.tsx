import { useMemo, useRef, useState, type DragEvent, type FormEvent } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { CloudUpload, ImagePlus, X } from "lucide-react";

import { PageTransition } from "../components/PageTransition";
import { useToast } from "../components/Toast";
import { ApiError, api } from "../lib/api";

const MAX_DESCRIPTION = 4096;
const MAX_FILES = 5;
const MAX_TOTAL_BYTES = 4 * 1024 * 1024;

function formatBytes(value: number) {
  if (value < 1024) return `${value} Б`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} КБ`;
  return `${(value / (1024 * 1024)).toFixed(1)} МБ`;
}

export function SupportPage() {
  const toast = useToast();
  const inputRef = useRef<HTMLInputElement>(null);
  const [contact, setContact] = useState("");
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [dragging, setDragging] = useState(false);
  const [sent, setSent] = useState(false);

  const configQuery = useQuery({
    queryKey: ["support-config"],
    queryFn: api.supportConfig,
  });
  const telegramUrl = configQuery.data?.telegram_url;

  const totalBytes = useMemo(
    () => files.reduce((sum, file) => sum + file.size, 0),
    [files],
  );

  const submitMutation = useMutation({
    mutationFn: () =>
      api.createSupportTicket({
        contact: contact.trim(),
        subject: subject.trim(),
        description: description.trim(),
        files,
      }),
    onSuccess: () => {
      setSent(true);
      setContact("");
      setSubject("");
      setDescription("");
      setFiles([]);
      toast("Обращение отправлено", "success");
    },
    onError: (error) => {
      toast(
        error instanceof ApiError ? error.message : "Не удалось отправить",
        "error",
      );
    },
  });

  const addFiles = (incoming: FileList | File[]) => {
    const next = [...files];
    for (const file of Array.from(incoming)) {
      if (!file.type.startsWith("image/")) {
        toast("Можно загружать только изображения", "error");
        continue;
      }
      if (next.length >= MAX_FILES) {
        toast(`Не больше ${MAX_FILES} файлов`, "error");
        break;
      }
      const projected = next.reduce((sum, item) => sum + item.size, 0) + file.size;
      if (projected > MAX_TOTAL_BYTES) {
        toast("Общий размер файлов не больше 4 МБ", "error");
        break;
      }
      next.push(file);
    }
    setFiles(next);
  };

  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragging(false);
    if (event.dataTransfer.files?.length) {
      addFiles(event.dataTransfer.files);
    }
  };

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!contact.trim() || !subject.trim() || !description.trim()) {
      toast("Заполните обязательные поля", "error");
      return;
    }
    if (description.trim().length > MAX_DESCRIPTION) {
      toast("Описание слишком длинное", "error");
      return;
    }
    submitMutation.mutate();
  };

  return (
    <PageTransition>
      <div className="mx-auto max-w-2xl pt-10 pb-8 sm:pt-14">
        <h1 className="font-display text-3xl tracking-tight sm:text-4xl">
          Поддержка <span className="text-glow-violet">Pixelgift</span>
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-slate-400">
          Ещё быстрее мы ответим в телеграме
          {telegramUrl ? (
            <>
              {" "}
              —{" "}
              <a
                href={telegramUrl}
                target="_blank"
                rel="noreferrer"
                className="text-glow-cyan underline-offset-2 hover:underline"
              >
                напишите нам
              </a>
            </>
          ) : null}
        </p>

        {sent ? (
          <div className="glass mt-10 p-8 text-center">
            <p className="font-display text-xl">Спасибо!</p>
            <p className="mt-3 text-sm text-slate-400">
              Обращение принято. Мы свяжемся с вами, если понадобится уточнение.
            </p>
            <button
              type="button"
              className="btn-primary mt-6"
              onClick={() => setSent(false)}
            >
              Отправить ещё одно
            </button>
          </div>
        ) : (
          <form className="mt-10 space-y-7" onSubmit={onSubmit}>
            <div>
              <label className="label" htmlFor="support-contact">
                Контакт <span className="text-rose-400">*</span>
              </label>
              <p className="mb-2 text-xs text-slate-500">
                Введите ваш email или телеграм
              </p>
              <input
                id="support-contact"
                className="field"
                value={contact}
                onChange={(event) => setContact(event.target.value)}
                placeholder="@username или you@mail.com"
                maxLength={254}
                required
              />
            </div>

            <div>
              <label className="label" htmlFor="support-subject">
                Тема <span className="text-rose-400">*</span>
              </label>
              <input
                id="support-subject"
                className="field"
                value={subject}
                onChange={(event) => setSubject(event.target.value)}
                maxLength={200}
                required
              />
            </div>

            <div>
              <label className="label" htmlFor="support-description">
                Описание <span className="text-rose-400">*</span>
              </label>
              <p className="mb-2 text-xs text-slate-500">
                Пожалуйста, опишите суть вашего запроса. Сотрудник технической
                поддержки свяжется с вами при необходимости
              </p>
              <textarea
                id="support-description"
                className="field min-h-40 resize-y"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                maxLength={MAX_DESCRIPTION}
                required
              />
              <p className="mt-1.5 text-right text-xs text-slate-500">
                {description.length}/{MAX_DESCRIPTION}
              </p>
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between gap-3">
                <label className="label mb-0">Изображения</label>
                <span className="text-xs text-slate-500">
                  До {MAX_FILES} файлов, общий размер до 4 МБ
                </span>
              </div>
              <div
                role="button"
                tabIndex={0}
                className={`glass-soft flex cursor-pointer flex-col items-center justify-center gap-3 border-dashed px-4 py-10 text-center transition ${
                  dragging
                    ? "border-glow-violet/50 bg-glow-violet/10"
                    : "hover:border-white/20"
                }`}
                onClick={() => inputRef.current?.click()}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    inputRef.current?.click();
                  }
                }}
                onDragOver={(event) => {
                  event.preventDefault();
                  setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={onDrop}
              >
                <CloudUpload className="size-8 text-glow-violet" />
                <p className="text-sm text-slate-300">
                  Перетащите изображения сюда или нажмите для выбора
                </p>
                <p className="inline-flex items-center gap-1.5 text-xs text-slate-500">
                  <ImagePlus className="size-3.5" />
                  до {MAX_FILES} · {formatBytes(totalBytes)} / 4 МБ
                </p>
                <input
                  ref={inputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp,image/gif"
                  multiple
                  className="hidden"
                  onChange={(event) => {
                    if (event.target.files) addFiles(event.target.files);
                    event.target.value = "";
                  }}
                />
              </div>

              {files.length > 0 ? (
                <ul className="mt-3 space-y-2">
                  {files.map((file, index) => (
                    <li
                      key={`${file.name}-${file.size}-${index}`}
                      className="flex items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-sm"
                    >
                      <span className="min-w-0 truncate text-slate-300">
                        {file.name}
                        <span className="ml-2 text-xs text-slate-500">
                          {formatBytes(file.size)}
                        </span>
                      </span>
                      <button
                        type="button"
                        className="grid size-7 place-items-center rounded-lg text-slate-400 hover:bg-white/10 hover:text-slate-100"
                        onClick={() =>
                          setFiles((current) =>
                            current.filter((_, itemIndex) => itemIndex !== index),
                          )
                        }
                        aria-label="Удалить файл"
                      >
                        <X className="size-4" />
                      </button>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>

            <button
              type="submit"
              className="btn-primary w-full justify-center uppercase tracking-wide"
              disabled={submitMutation.isPending}
            >
              {submitMutation.isPending ? "Отправляем…" : "Отправить"}
            </button>
          </form>
        )}
      </div>
    </PageTransition>
  );
}
