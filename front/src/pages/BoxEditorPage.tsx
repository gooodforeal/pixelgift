import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  ArchiveRestore,
  Copy,
  ExternalLink,
  Lock,
  Rocket,
  Save,
  Trash2,
} from "lucide-react";

import {
  BOX_WIZARD_STEPS,
  BoxWizardProgress,
  isBoxWizardStepId,
  type BoxWizardStepId,
} from "../components/BoxWizardProgress";
import { DesignPicker } from "../components/DesignPicker";
import { MediaDropzone } from "../components/MediaDropzone";
import { MediaPreview } from "../components/MediaPreview";
import { PageTransition } from "../components/PageTransition";
import { Spinner } from "../components/Spinner";
import { StatusBadge } from "../components/StatusBadge";
import { useToast } from "../components/Toast";
import { api, ownMediaUrl } from "../lib/api";
import {
  MAX_BOX_ITEM_CAPTION,
  MAX_BOX_ITEMS,
  MAX_BOX_MESSAGE,
  MAX_BOX_PREVIEW_TITLE,
  MAX_BOX_RECIPIENT_NAME,
  MAX_BOX_TITLE,
} from "../lib/limits";
import {
  defaultActivatesAt,
  fromDateTimeLocal,
  joinDateTimeLocal,
  localTimezone,
  pluralize,
  splitDateTimeLocal,
  toDateTimeLocal,
} from "../lib/format";
import {
  formatGeopointCoords,
  geopointFromMetadata,
  type GeopointCoords,
} from "../lib/geopoint";
import { getMediaKindOption } from "../lib/mediaKinds";
import type { Box, BoxItemType, BoxPayload } from "../lib/types";
import { getToyOption, toyCodeFromMetadata, toyImageUrl } from "../lib/toys";

interface FormState {
  design_id: string;
  title: string;
  recipient_name: string;
  activates_at_local: string;
  message: string;
  preview_title: string;
}

const emptyForm: FormState = {
  design_id: "",
  title: "",
  recipient_name: "",
  activates_at_local: defaultActivatesAt(),
  message: "",
  preview_title: "",
};

function toPayload(form: FormState): BoxPayload {
  return {
    design_id: form.design_id,
    title: form.title.trim(),
    recipient_name: form.recipient_name.trim(),
    activates_at: fromDateTimeLocal(form.activates_at_local),
    timezone: localTimezone,
    message: form.message.trim() || null,
    preview_title: form.preview_title.trim() || null,
  };
}

function stepIndex(id: BoxWizardStepId): number {
  return BOX_WIZARD_STEPS.findIndex((step) => step.id === id);
}

function formDirty(form: FormState, box: Box | undefined): boolean {
  if (!box) return true;
  return (
    form.design_id !== box.design_id ||
    form.title !== box.title ||
    form.recipient_name !== box.recipient_name ||
    form.activates_at_local !== toDateTimeLocal(box.activates_at) ||
    form.message !== (box.message ?? "") ||
    form.preview_title !== (box.preview_title ?? "")
  );
}

export function BoxEditorPage() {
  const { boxId } = useParams<{ boxId: string }>();
  const isNew = !boxId;
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const toast = useToast();
  const queryClient = useQueryClient();

  const [form, setForm] = useState<FormState>(emptyForm);
  const [uploadKind, setUploadKind] = useState<BoxItemType>("image");

  const stepParam = searchParams.get("step");
  const step: BoxWizardStepId =
    isBoxWizardStepId(stepParam) && !(isNew && (stepParam === "content" || stepParam === "publish"))
      ? stepParam
      : "design";

  const setStep = (next: BoxWizardStepId) => {
    setSearchParams(
      (current) => {
        const params = new URLSearchParams(current);
        params.set("step", next);
        return params;
      },
      { replace: true },
    );
  };

  const designsQuery = useQuery({ queryKey: ["designs"], queryFn: api.designs });
  const boxQuery = useQuery({
    queryKey: ["box", boxId],
    queryFn: () => api.box(boxId!),
    enabled: !isNew,
  });

  const box = boxQuery.data;

  useEffect(() => {
    if (box) {
      setForm({
        design_id: box.design_id,
        title: box.title,
        recipient_name: box.recipient_name,
        activates_at_local: toDateTimeLocal(box.activates_at),
        message: box.message ?? "",
        preview_title: box.preview_title ?? "",
      });
    }
  }, [box]);

  useEffect(() => {
    const designs = designsQuery.data;
    if (isNew && designs && designs.length > 0) {
      setForm((current) =>
        current.design_id ? current : { ...current, design_id: designs[0].id },
      );
    }
  }, [designsQuery.data, isNew]);

  const setBoxData = (updated: Box) => {
    queryClient.setQueryData(["box", updated.id], updated);
    queryClient.invalidateQueries({ queryKey: ["boxes"] });
  };

  const createBox = useMutation({
    mutationFn: () => api.createBox(toPayload(form)),
    onSuccess: (created) => {
      setBoxData(created);
      toast("Черновик создан — добавьте медиа");
      navigate(`/app/boxes/${created.id}?step=content`, { replace: true });
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const saveBox = useMutation({
    mutationFn: () => api.updateBox(boxId!, toPayload(form)),
    onSuccess: (updated) => {
      setBoxData(updated);
      toast("Изменения сохранены");
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const uploadFiles = useMutation({
    mutationFn: async (files: File[]) => {
      let latest: Box | null = null;
      for (const file of files.slice(0, 10)) {
        const media = await api.uploadMedia(file, uploadKind);
        latest = await api.addItem(boxId!, media.id);
      }
      return latest;
    },
    onSuccess: (updated) => {
      if (updated) setBoxData(updated);
      toast("Медиа добавлено в бокс");
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const addTextItem = useMutation({
    mutationFn: (text: string) => api.addTextItem(boxId!, text),
    onSuccess: (updated) => {
      setBoxData(updated);
      toast("Текст добавлен в бокс");
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const addDrawingItem = useMutation({
    mutationFn: async (blob: Blob) => {
      const file = new File([blob], `drawing-${Date.now()}.png`, {
        type: "image/png",
      });
      const media = await api.uploadMedia(file, "image");
      return api.addItem(boxId!, media.id, null, "drawing");
    },
    onSuccess: (updated) => {
      setBoxData(updated);
      toast("Рисунок добавлен в бокс");
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const addToyItem = useMutation({
    mutationFn: (input: { toyCode: string; caption: string }) =>
      api.addToyItem(boxId!, input.toyCode, input.caption || null),
    onSuccess: (updated) => {
      setBoxData(updated);
      toast("Игрушка добавлена в бокс");
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const addGeopointItem = useMutation({
    mutationFn: (input: { coords: GeopointCoords; caption: string }) =>
      api.addGeopointItem(boxId!, input.coords, input.caption || null),
    onSuccess: (updated) => {
      setBoxData(updated);
      toast("Геоточка добавлена в бокс");
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const updateCaption = useMutation({
    mutationFn: (input: { itemId: string; caption: string | null }) =>
      api.updateItem(boxId!, input.itemId, input.caption),
    onSuccess: setBoxData,
    onError: (error: Error) => toast(error.message, "error"),
  });

  const removeItem = useMutation({
    mutationFn: (itemId: string) => api.removeItem(boxId!, itemId),
    onSuccess: (updated) => {
      setBoxData(updated);
      toast("Файл удалён из бокса");
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const reorderItems = useMutation({
    mutationFn: (itemIds: string[]) => api.reorderItems(boxId!, itemIds),
    onSuccess: setBoxData,
    onError: (error: Error) => toast(error.message, "error"),
  });

  const publishBox = useMutation({
    mutationFn: () => api.publishBox(boxId!),
    onSuccess: (updated) => {
      setBoxData(updated);
      toast("Бокс опубликован — можно отправлять ссылку");
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const unarchiveBox = useMutation({
    mutationFn: () => api.unarchiveBox(boxId!),
    onSuccess: (updated) => {
      setBoxData(updated);
      toast("Бокс возвращён из архива");
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  const publicUrl = useMemo(
    () => (box ? `${window.location.origin}/b/${box.public_slug}` : ""),
    [box],
  );

  const move = (index: number, direction: -1 | 1) => {
    if (!box) return;
    const ids = box.items.map((item) => item.id);
    const target = index + direction;
    if (target < 0 || target >= ids.length) return;
    [ids[index], ids[target]] = [ids[target], ids[index]];
    reorderItems.mutate(ids);
  };

  const editable = !box || box.status === "draft" || box.status === "scheduled";
  const readOnly = Boolean(box && !editable);
  const freeSlots = Math.max(0, MAX_BOX_ITEMS - (box?.items.length ?? 0));
  const activatesParts = splitDateTimeLocal(form.activates_at_local);
  const canSubmitDetails =
    form.design_id.length > 0 &&
    form.title.trim().length > 0 &&
    form.recipient_name.trim().length > 0 &&
    activatesParts.date.length > 0 &&
    activatesParts.time.length > 0;

  const currentIndex = stepIndex(step);
  const maxReachableIndex = isNew
    ? currentIndex
    : BOX_WIZARD_STEPS.length - 1;

  const goNext = async () => {
    if (step === "design") {
      if (!form.design_id) {
        toast("Выберите тему оформления", "error");
        return;
      }
      setStep("details");
      return;
    }

    if (step === "details") {
      if (!canSubmitDetails) {
        toast("Заполните название, получателя и дату открытия", "error");
        return;
      }

      if (isNew) {
        createBox.mutate();
        return;
      }

      if (editable && formDirty(form, box)) {
        try {
          const updated = await saveBox.mutateAsync();
          setBoxData(updated);
        } catch {
          return;
        }
      }
      setStep("content");
      return;
    }

    if (step === "content") {
      setStep("publish");
    }
  };

  const handleSelectStep = (next: BoxWizardStepId) => {
    const nextIdx = stepIndex(next);
    if (nextIdx <= currentIndex) {
      setStep(next);
      return;
    }
    if (nextIdx === currentIndex + 1) {
      void goNext();
      return;
    }
    if (!isNew) setStep(next);
  };

  const goBack = () => {
    if (currentIndex <= 0) return;
    setStep(BOX_WIZARD_STEPS[currentIndex - 1].id);
  };

  const navBusy = createBox.isPending || saveBox.isPending;

  if (!isNew && boxQuery.isPending) {
    return <Spinner label="Загружаем бокс…" className="py-32" />;
  }

  if (!isNew && boxQuery.isError) {
    return (
      <div className="glass-soft mt-24 p-8 text-center text-sm text-rose-200">
        Не удалось открыть бокс: {(boxQuery.error as Error).message}
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="flex flex-wrap items-start justify-between gap-3 pt-6 pb-6 sm:items-center sm:gap-4 sm:pt-12 sm:pb-8">
        <div className="flex min-w-0 flex-1 items-start gap-2.5 sm:items-center sm:gap-3">
          <Link to="/app" className="btn-ghost mt-0.5 size-10 shrink-0 px-0! sm:mt-0">
            <ArrowLeft className="size-4" />
          </Link>
          <div className="min-w-0">
            <h1 className="font-sans font-semibold truncate text-xl tracking-tight sm:text-3xl">
              {isNew ? "Новый бокс" : box?.title}
            </h1>
            <p className="mt-1 line-clamp-2 text-xs text-slate-400 sm:text-sm">
              {isNew
                ? "Соберите подарок за четыре шага"
                : readOnly
                  ? box?.status === "archived"
                    ? "Бокс в архиве — только просмотр"
                    : "Бокс уже открыт получателем — только просмотр"
                  : `Часовой пояс ${box?.timezone}`}
            </p>
          </div>
        </div>
        {box && <StatusBadge status={box.status} />}
      </div>

      <BoxWizardProgress
        current={step}
        maxReachableIndex={maxReachableIndex}
        onSelect={handleSelectStep}
      />

      {readOnly && (
        <div className="publish-hint mb-6 flex items-start gap-3 rounded-3xl border border-amber-400/25 bg-amber-400/10 px-5 py-4 text-sm text-amber-100">
          <Lock className="mt-0.5 size-4 shrink-0 text-amber-300" />
          <div>
            <p className="font-semibold">Редактирование недоступно</p>
            <p className="mt-1 opacity-85">
              {box?.status === "archived"
                ? box.first_opened_at
                  ? "Архивный бокс уже открывали — только просмотр."
                  : "Архивный бокс ещё не вручали. Можно вернуть из архива."
                : "После открытия подарка содержимое и настройки зафиксированы."}
            </p>
          </div>
        </div>
      )}

      <section className="glass overflow-hidden p-4 sm:p-6">
        {step === "design" && (
          <>
            {designsQuery.isPending ? (
              <Spinner label="Загружаем темы…" className="py-10" />
            ) : (
              <DesignPicker
                designs={designsQuery.data ?? []}
                selectedId={form.design_id}
                disabled={!editable}
                onSelect={(design_id) =>
                  setForm((current) => ({ ...current, design_id }))
                }
              />
            )}
          </>
        )}

        {step === "details" && (
          <div className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="label" htmlFor="title">
                  Заголовок бокса
                </label>
                <input
                  id="title"
                  className="field disabled:opacity-60"
                  maxLength={MAX_BOX_TITLE}
                  placeholder="С днём рождения!"
                  disabled={!editable}
                  value={form.title}
                  onChange={(event) =>
                    setForm((current) => ({ ...current, title: event.target.value }))
                  }
                />
              </div>
              <div>
                <label className="label" htmlFor="recipient">
                  Кому
                </label>
                <input
                  id="recipient"
                  className="field disabled:opacity-60"
                  maxLength={MAX_BOX_RECIPIENT_NAME}
                  placeholder="Аня"
                  disabled={!editable}
                  value={form.recipient_name}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      recipient_name: event.target.value,
                    }))
                  }
                />
              </div>
              <div>
                <label className="label" htmlFor="activates-date">
                  Дата открытия
                </label>
                <input
                  id="activates-date"
                  type="date"
                  className="field disabled:opacity-60"
                  disabled={!editable}
                  value={activatesParts.date}
                  onChange={(event) =>
                    setForm((current) => {
                      const currentTime =
                        splitDateTimeLocal(current.activates_at_local).time || "12:00";
                      return {
                        ...current,
                        activates_at_local: joinDateTimeLocal(
                          event.target.value,
                          currentTime,
                        ),
                      };
                    })
                  }
                />
              </div>
              <div>
                <label className="label" htmlFor="activates-time">
                  Время открытия
                </label>
                <input
                  id="activates-time"
                  type="time"
                  className="field disabled:opacity-60"
                  disabled={!editable}
                  value={activatesParts.time}
                  onChange={(event) =>
                    setForm((current) => {
                      const currentDate = splitDateTimeLocal(
                        current.activates_at_local,
                      ).date;
                      if (!currentDate) return current;
                      return {
                        ...current,
                        activates_at_local: joinDateTimeLocal(
                          currentDate,
                          event.target.value,
                        ),
                      };
                    })
                  }
                />
                <p className="mt-2 text-xs text-slate-500">
                  По вашему часовому поясу ({localTimezone})
                </p>
              </div>
            </div>

            <div>
              <label className="label" htmlFor="preview-title">
                Что видно до открытия
              </label>
              <input
                id="preview-title"
                className="field disabled:opacity-60"
                maxLength={MAX_BOX_PREVIEW_TITLE}
                placeholder="Для тебя приготовлен подарок…"
                disabled={!editable}
                value={form.preview_title}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    preview_title: event.target.value,
                  }))
                }
              />
            </div>

            <div>
              <label className="label" htmlFor="message">
                Письмо внутри бокса
              </label>
              <textarea
                id="message"
                className="field min-h-28 resize-y disabled:opacity-60"
                maxLength={MAX_BOX_MESSAGE}
                placeholder="Пара тёплых слов, которые получатель прочитает первыми…"
                disabled={!editable}
                value={form.message}
                onChange={(event) =>
                  setForm((current) => ({ ...current, message: event.target.value }))
                }
              />
              <p className="mt-2 text-right text-xs text-slate-500">
                {form.message.length}/{MAX_BOX_MESSAGE}
              </p>
            </div>

            {!isNew && editable && (
              <button
                type="button"
                className="btn-ghost"
                disabled={!canSubmitDetails || saveBox.isPending}
                onClick={() => saveBox.mutate()}
              >
                <Save className="size-4" />
                Сохранить без перехода
              </button>
            )}
          </div>
        )}

        {step === "content" && box && (
          <>
            <div className="flex items-baseline justify-between gap-3">
              <h2 className="font-sans font-semibold text-lg">Карточки в боксе</h2>
              <span className="text-xs text-slate-500">
                {box.items.length} из {MAX_BOX_ITEMS}{" "}
                {pluralize(MAX_BOX_ITEMS, ["карточки", "карточек", "карточек"])}
              </span>
            </div>

            {editable && (
              <div className="mt-5">
                <MediaDropzone
                  kind={uploadKind}
                  onKindChange={setUploadKind}
                  disabled={freeSlots === 0}
                  onFiles={(files) => {
                    if (files.length > freeSlots) {
                      toast(
                        `Осталось мест: ${freeSlots}. Добавим первые ${freeSlots}.`,
                        "error",
                      );
                    }
                    uploadFiles.mutate(files.slice(0, freeSlots));
                  }}
                  onAddText={(text) => addTextItem.mutate(text)}
                  onAddDrawing={(blob) => addDrawingItem.mutate(blob)}
                  onAddToy={(toyCode, caption) =>
                    addToyItem.mutate({ toyCode, caption })
                  }
                  onAddGeopoint={(coords, caption) =>
                    addGeopointItem.mutate({ coords, caption })
                  }
                  onRejected={(files, kind) => {
                    const option = getMediaKindOption(kind);
                    toast(
                      `Не подходит для «${option.label}»: ${files
                        .map((file) => file.name)
                        .slice(0, 3)
                        .join(", ")}${files.length > 3 ? "…" : ""}. Нужно: ${option.hint}`,
                      "error",
                    );
                  }}
                  uploading={
                    uploadFiles.isPending ||
                    addTextItem.isPending ||
                    addDrawingItem.isPending ||
                    addToyItem.isPending ||
                    addGeopointItem.isPending
                  }
                />
                {freeSlots === 0 && (
                  <p className="publish-hint mt-4 rounded-2xl border border-amber-400/25 bg-amber-400/10 px-3 py-2 text-xs text-amber-100">
                    Достигнут лимит — {MAX_BOX_ITEMS} карточек в одном боксе. Удалите
                    лишнее, чтобы добавить новое.
                  </p>
                )}
              </div>
            )}

            <div className="mt-5 space-y-3">
              <AnimatePresence initial={false}>
                {box.items.map((item, index) => (
                  <motion.div
                    key={item.id}
                    layout
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.97 }}
                    className="glass-soft flex gap-3 p-3"
                  >
                    <div className="size-20 shrink-0 overflow-hidden rounded-2xl bg-ink-800">
                      {item.item_type === "text" ? (
                        <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-glow-violet/25 to-glow-cyan/15 p-2 text-center text-[0.65rem] leading-snug text-slate-200">
                          {(item.caption ?? "Текст").slice(0, 48)}
                          {(item.caption?.length ?? 0) > 48 ? "…" : ""}
                        </div>
                      ) : item.item_type === "toy" ? (
                        <img
                          src={toyImageUrl(
                            toyCodeFromMetadata(item.metadata) ?? "bear",
                          )}
                          alt={
                            getToyOption(toyCodeFromMetadata(item.metadata))
                              ?.name ?? "Игрушка"
                          }
                          className="h-full w-full object-cover"
                        />
                      ) : item.item_type === "geopoint" ? (
                        (() => {
                          const point = geopointFromMetadata(item.metadata);
                          return (
                            <div className="flex h-full w-full flex-col items-center justify-center gap-1 bg-gradient-to-br from-emerald-500/20 to-sky-500/15 p-2 text-center">
                              <span className="text-lg leading-none">📍</span>
                              <span className="line-clamp-2 text-[0.6rem] leading-snug text-slate-200">
                                {point
                                  ? formatGeopointCoords(point)
                                  : "Точка"}
                              </span>
                            </div>
                          );
                        })()
                      ) : item.media_file_id ? (
                        <MediaPreview
                          src={ownMediaUrl(item.media_file_id)}
                          type={item.item_type}
                          fit="cover"
                        />
                      ) : null}
                    </div>

                    <div className="min-w-0 flex-1">
                      {editable ? (
                        <>
                          <input
                            className="field py-2! text-xs"
                            maxLength={MAX_BOX_ITEM_CAPTION}
                                placeholder={
                                  item.item_type === "text"
                                    ? "Текст карточки"
                                    : item.item_type === "toy"
                                      ? "Подпись к игрушке"
                                      : item.item_type === "geopoint"
                                        ? "Подпись к точке"
                                        : item.item_type === "drawing"
                                          ? "Подпись к рисунку"
                                        : "Подпись к файлу"
                                }
                            defaultValue={item.caption ?? ""}
                            onBlur={(event) => {
                              const value = event.target.value.trim();
                              if (value !== (item.caption ?? "")) {
                                if (item.item_type === "text" && !value) {
                                  toast("Текст не может быть пустым", "error");
                                  event.target.value = item.caption ?? "";
                                  return;
                                }
                                updateCaption.mutate({
                                  itemId: item.id,
                                  caption: value || null,
                                });
                              }
                            }}
                          />
                          <div className="mt-2 flex items-center gap-1.5">
                            <button
                              type="button"
                              className="btn-ghost size-8 px-0!"
                              disabled={index === 0}
                              onClick={() => move(index, -1)}
                            >
                              <ArrowUp className="size-3.5" />
                            </button>
                            <button
                              type="button"
                              className="btn-ghost size-8 px-0!"
                              disabled={index === box.items.length - 1}
                              onClick={() => move(index, 1)}
                            >
                              <ArrowDown className="size-3.5" />
                            </button>
                            <button
                              type="button"
                              className="btn-danger ml-auto size-8 px-0!"
                              onClick={() => removeItem.mutate(item.id)}
                            >
                              <Trash2 className="size-3.5" />
                            </button>
                          </div>
                        </>
                      ) : (
                        <p className="text-sm leading-relaxed text-slate-300">
                          {item.caption || (
                            <span className="text-slate-500">Без подписи</span>
                          )}
                        </p>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {box.items.length === 0 && (
                <p className="text-sm text-slate-500">В боксе пока нет медиа.</p>
              )}
            </div>
          </>
        )}

        {step === "publish" && box && (
          <>
            <p className="text-sm text-slate-400">
              {box.status === "draft"
                ? "Пока бокс — черновик, ссылка не работает."
                : box.status === "archived"
                  ? "Бокс в архиве: публичная ссылка больше не открывает подарок."
                  : box.status === "active"
                    ? "Бокс уже открывали — содержимое доступно по ссылке."
                    : "Бокс опубликован: ссылка открывает превью и таймер."}
            </p>

            <div className="editor-slug-field mt-4 flex items-center gap-2 rounded-2xl border border-white/10 bg-ink-900/70 px-4 py-3">
              <span className="truncate font-mono text-xs text-slate-300">
                {publicUrl}
              </span>
              <button
                type="button"
                className="btn-ghost ml-auto size-8 shrink-0 px-0!"
                onClick={async () => {
                  await navigator.clipboard.writeText(publicUrl);
                  toast("Ссылка скопирована");
                }}
              >
                <Copy className="size-3.5" />
              </button>
            </div>

            <div className="mt-5 flex flex-wrap gap-2">
              {box.status === "draft" && (
                <button
                  type="button"
                  className="btn-primary"
                  disabled={publishBox.isPending || box.items.length === 0}
                  onClick={() => publishBox.mutate()}
                >
                  <Rocket className="size-4" />
                  Опубликовать
                </button>
              )}
              {box.status === "archived" && box.first_opened_at == null && (
                <button
                  type="button"
                  className="btn-primary"
                  disabled={unarchiveBox.isPending}
                  onClick={() => unarchiveBox.mutate()}
                >
                  <ArchiveRestore className="size-4" />
                  Вернуть из архива
                </button>
              )}
              <a
                href={`/b/${box.public_slug}`}
                target="_blank"
                rel="noreferrer"
                className="btn-ghost"
              >
                <ExternalLink className="size-4" />
                Посмотреть глазами получателя
              </a>
            </div>

            {box.status === "draft" && box.items.length === 0 && (
              <p className="publish-hint mt-4 rounded-2xl border border-amber-400/25 bg-amber-400/10 px-3 py-2 text-xs text-amber-100">
                Добавьте хотя бы один файл — иначе публикация недоступна.
              </p>
            )}
          </>
        )}

        <div className="box-wizard__nav">
          <button
            type="button"
            className="btn-ghost"
            disabled={currentIndex === 0 || navBusy}
            onClick={goBack}
          >
            <ArrowLeft className="size-4" />
            Назад
          </button>

          {step !== "publish" ? (
            <button
              type="button"
              className="btn-primary"
              disabled={
                navBusy ||
                (step === "design" && !form.design_id) ||
                (step === "details" && !canSubmitDetails && editable) ||
                (step === "content" && !box)
              }
              onClick={() => {
                void goNext();
              }}
            >
              {step === "details" && isNew
                ? createBox.isPending
                  ? "Создаём…"
                  : "Создать и далее"
                : step === "details" && saveBox.isPending
                  ? "Сохраняем…"
                  : "Далее"}
              <ArrowRight className="size-4" />
            </button>
          ) : (
            <Link to="/app" className="btn-ghost">
              К списку боксов
            </Link>
          )}
        </div>
      </section>
    </PageTransition>
  );
}
