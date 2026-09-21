import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ImagePlus, Save, Trash2 } from "lucide-react";

import { designCoverUrl } from "../components/DesignCover";
import { ColorSwatch } from "../components/ColorSwatch";
import { DesignGiftPreview } from "../components/DesignGiftPreview";
import { PageTransition } from "../components/PageTransition";
import { ParticleSelect } from "../components/ParticleSelect";
import { Spinner } from "../components/Spinner";
import { ToggleSwitch } from "../components/ToggleSwitch";
import { api, type AdminDesignPayload } from "../lib/api";
import {
  DESIGN_CODE_MAX,
  DESIGN_DESCRIPTION_MAX,
  DESIGN_NAME_MAX,
} from "../lib/designLimits";
import { gradientCss, resolveTheme } from "../lib/theme";
import type { AdminBoxDesign, ThemeConfig } from "../lib/types";
import { useUiTheme } from "../hooks/useUiTheme";

const DEFAULT_COVER_POSITION = "50% 50%";

const EMPTY_GIFT_BOX = {
  body: "#f0a8c8",
  bodyDark: "#b4487a",
  lid: "#f4b8d4",
  lidLight: "#ffd9ea",
  ribbon: "#ffd775",
  ribbonDark: "#b8820f",
};

const PLACEHOLDER_PREVIEW_URL = "";

function blankForm(): AdminDesignPayload {
  return {
    code: "",
    name: "",
    preview_image_url: PLACEHOLDER_PREVIEW_URL,
    description: null,
    is_active: true,
    sort_order: 1,
    theme_config: {
      gradient: ["#1e1b4b", "#4c1d95", "#831843"],
      accent: "#f472b6",
      text: "#fdf2f8",
      particle: "sparkle",
      cover_object_position: DEFAULT_COVER_POSITION,
      background_image_url: null,
      preview_image_url_light: null,
      gift_box: { ...EMPTY_GIFT_BOX },
    },
  };
}

function fromDesign(design: AdminBoxDesign): AdminDesignPayload {
  const theme = design.theme_config ?? {};
  return {
    code: design.code,
    name: design.name,
    preview_image_url: design.preview_image_url,
    description: design.description,
    is_active: design.is_active,
    sort_order: design.sort_order,
    theme_config: {
      gradient: theme.gradient?.length
        ? [...theme.gradient]
        : ["#1e1b4b", "#4c1d95", "#831843"],
      accent: theme.accent ?? "#f472b6",
      text: theme.text ?? "#fdf2f8",
      particle: theme.particle ?? "sparkle",
      cover_object_position: DEFAULT_COVER_POSITION,
      background_image_url: theme.background_image_url ?? null,
      preview_image_url_light: theme.preview_image_url_light ?? null,
      gift_box: { ...EMPTY_GIFT_BOX, ...theme.gift_box },
    },
  };
}

export function AdminDesignEditorPage() {
  const { designId } = useParams<{ designId: string }>();
  const isNew = !designId || designId === "new";
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const designQuery = useQuery({
    queryKey: ["admin-design", designId],
    queryFn: () => api.adminDesign(designId!),
    enabled: !isNew,
  });

  const { theme: uiTheme } = useUiTheme();
  const [form, setForm] = useState<AdminDesignPayload>(blankForm);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<
    "preview" | "preview_light" | "background" | null
  >(null);

  useEffect(() => {
    if (designQuery.data) {
      setForm(fromDesign(designQuery.data));
    }
  }, [designQuery.data]);

  const previewDesign = useMemo<AdminBoxDesign>(
    () => ({
      id: designId ?? "preview",
      code: form.code || "preview",
      name: form.name || "Превью",
      preview_image_url: form.preview_image_url,
      sort_order: form.sort_order,
      description: form.description,
      is_active: form.is_active,
      theme_config: form.theme_config,
      rating_avg: 0,
      rating_count: 0,
      my_rating: null,
    }),
    [designId, form],
  );

  const hasPreviewImage =
    Boolean(form.preview_image_url) &&
    form.preview_image_url !== PLACEHOLDER_PREVIEW_URL;
  const hasLightPreview = Boolean(form.theme_config.preview_image_url_light);

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!hasPreviewImage) {
        throw new Error("Загрузите обложку дизайна");
      }
      const payload: AdminDesignPayload = {
        ...form,
        description: form.description?.trim() ? form.description.trim() : null,
        theme_config: {
          ...form.theme_config,
          cover_object_position: DEFAULT_COVER_POSITION,
        },
      };
      if (isNew) {
        return api.createAdminDesign(payload);
      }
      return api.updateAdminDesign(designId!, payload);
    },
    onSuccess: (design) => {
      void queryClient.invalidateQueries({ queryKey: ["admin-designs"] });
      void queryClient.invalidateQueries({ queryKey: ["designs"] });
      void queryClient.invalidateQueries({ queryKey: ["admin-design", design.id] });
      navigate(`/app/panel/designs/${design.id}`, { replace: true });
    },
    onError: (err) => setError((err as Error).message),
  });

  async function uploadImage(
    kind: "preview" | "preview_light" | "background",
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setUploading(kind);
    setError(null);
    try {
      const asset = await api.uploadDesignAsset(file);
      if (kind === "preview") {
        setForm((current) => ({ ...current, preview_image_url: asset.url }));
      } else if (kind === "preview_light") {
        setTheme({ preview_image_url_light: asset.url });
      } else {
        setTheme({ background_image_url: asset.url });
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setUploading(null);
    }
  }

  function setTheme(patch: Partial<ThemeConfig>) {
    setForm((current) => ({
      ...current,
      theme_config: { ...current.theme_config, ...patch },
    }));
  }

  function setGradient(index: number, value: string) {
    const gradient = [...(form.theme_config.gradient ?? ["#000", "#111", "#222"])];
    gradient[index] = value;
    setTheme({ gradient });
  }

  function setGiftBox(key: keyof typeof EMPTY_GIFT_BOX, value: string) {
    setTheme({
      gift_box: {
        ...EMPTY_GIFT_BOX,
        ...form.theme_config.gift_box,
        [key]: value,
      },
    });
  }

  if (!isNew && designQuery.isPending) {
    return <Spinner label="Загружаем дизайн…" className="py-32" />;
  }

  if (!isNew && designQuery.isError) {
    return (
      <PageTransition>
        <div className="glass-soft mt-16 p-8 text-center text-sm text-rose-200">
          {(designQuery.error as Error).message}
        </div>
      </PageTransition>
    );
  }

  const gift = { ...EMPTY_GIFT_BOX, ...form.theme_config.gift_box };
  const bannerTheme = resolveTheme(previewDesign);
  const bannerCover = designCoverUrl(previewDesign, uiTheme);

  return (
    <PageTransition>
      <div className="pt-10 pb-10 sm:pt-14">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link
            to="/app/panel/designs"
            className="btn-ghost inline-flex items-center gap-2 px-3 py-2 text-sm"
          >
            <ArrowLeft className="size-4" />
            К списку
          </Link>
          <button
            type="button"
            className="btn-primary"
            disabled={saveMutation.isPending}
            onClick={() => {
              setError(null);
              saveMutation.mutate();
            }}
          >
            <Save className="size-4" />
            {saveMutation.isPending ? "Сохраняем…" : "Сохранить"}
          </button>
        </div>

        <h1 className="mt-6 font-sans text-2xl font-semibold tracking-tight sm:text-3xl">
          {isNew ? "Новый дизайн" : form.name || "Редактирование"}
        </h1>

        {error ? (
          <p className="mt-4 rounded-xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
            {error}
          </p>
        ) : null}

        <div className="mt-8 grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(280px,360px)]">
          <div className="space-y-6">
            <section className="glass space-y-4 p-5 sm:p-6">
              <h2 className="font-sans text-sm font-semibold tracking-wide text-slate-200 uppercase">
                Метаданные
              </h2>
              <label className="flex flex-col gap-3 text-sm">
                <span className="text-slate-400">Code</span>
                <input
                  className="field"
                  value={form.code}
                  maxLength={DESIGN_CODE_MAX}
                  onChange={(e) => setForm({ ...form, code: e.target.value })}
                  placeholder="romantic"
                />
              </label>
              <label className="flex flex-col gap-3 text-sm">
                <span className="text-slate-400">Название</span>
                <input
                  className="field"
                  value={form.name}
                  maxLength={DESIGN_NAME_MAX}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </label>
              <label className="flex flex-col gap-3 text-sm">
                <span className="text-slate-400">Описание</span>
                <textarea
                  className="field min-h-24 resize-y"
                  value={form.description ?? ""}
                  maxLength={DESIGN_DESCRIPTION_MAX}
                  onChange={(e) =>
                    setForm({ ...form, description: e.target.value || null })
                  }
                />
              </label>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="flex flex-col gap-3 text-sm">
                  <span className="text-slate-400">Порядок</span>
                  <input
                    type="number"
                    min={1}
                    className="field"
                    value={form.sort_order}
                    onChange={(e) =>
                      setForm({ ...form, sort_order: Number(e.target.value) || 1 })
                    }
                  />
                </label>
                <div className="flex items-end pb-2">
                  <ToggleSwitch
                    checked={form.is_active}
                    label="Активен"
                    onChange={(is_active) => setForm({ ...form, is_active })}
                  />
                </div>
              </div>
            </section>

            <section className="glass space-y-4 p-5 sm:p-6">
              <h2 className="font-sans text-sm font-semibold tracking-wide text-slate-200 uppercase">
                Обложка и фон
              </h2>
              <div className="flex flex-wrap items-center gap-3">
                <label className="btn-ghost inline-flex cursor-pointer items-center gap-2 px-3 py-2 text-sm">
                  <ImagePlus className="size-4" />
                  {uploading === "preview" ? "Загрузка…" : "Обложка (тёмная)"}
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    disabled={uploading !== null}
                    onChange={(e) => void uploadImage("preview", e)}
                  />
                </label>
                <label className="btn-ghost inline-flex cursor-pointer items-center gap-2 px-3 py-2 text-sm">
                  <ImagePlus className="size-4" />
                  {uploading === "preview_light" ? "Загрузка…" : "Обложка (светлая)"}
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    disabled={uploading !== null}
                    onChange={(e) => void uploadImage("preview_light", e)}
                  />
                </label>
                {hasLightPreview ? (
                  <button
                    type="button"
                    className="btn-ghost inline-flex items-center gap-2 px-3 py-2 text-sm text-rose-200"
                    onClick={() => setTheme({ preview_image_url_light: null })}
                  >
                    <Trash2 className="size-4" />
                    Убрать светлую
                  </button>
                ) : null}
                <label className="btn-ghost inline-flex cursor-pointer items-center gap-2 px-3 py-2 text-sm">
                  <ImagePlus className="size-4" />
                  {uploading === "background" ? "Загрузка…" : "Фон страницы"}
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    disabled={uploading !== null}
                    onChange={(e) => void uploadImage("background", e)}
                  />
                </label>
                {form.theme_config.background_image_url ? (
                  <button
                    type="button"
                    className="btn-ghost inline-flex items-center gap-2 px-3 py-2 text-sm text-rose-200"
                    onClick={() => setTheme({ background_image_url: null })}
                  >
                    <Trash2 className="size-4" />
                    Убрать фон
                  </button>
                ) : null}
              </div>
              <p className="text-xs text-slate-500">
                {hasPreviewImage
                  ? "Тёмная обложка задана — ссылка подставится сама."
                  : "Загрузите тёмную обложку — без неё дизайн не сохранится."}{" "}
                {hasLightPreview
                  ? "Светлая обложка задана."
                  : "Светлая обложка необязательна: без неё будет тёмная."}
                {form.theme_config.background_image_url
                  ? " Фон страницы задан."
                  : " Фон необязателен."}
              </p>
            </section>

            <section className="glass space-y-4 p-5 sm:p-6">
              <h2 className="font-sans text-sm font-semibold tracking-wide text-slate-200 uppercase">
                Цвета темы
              </h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {(form.theme_config.gradient ?? ["#000", "#111", "#222"]).map(
                  (color, index) => (
                    <ColorSwatch
                      key={index}
                      label={`Gradient ${index + 1}`}
                      value={color}
                      onChange={(value) => setGradient(index, value)}
                    />
                  ),
                )}
                <ColorSwatch
                  label="Accent"
                  value={form.theme_config.accent ?? "#f472b6"}
                  onChange={(value) => setTheme({ accent: value })}
                />
                <ColorSwatch
                  label="Text"
                  value={form.theme_config.text ?? "#fdf2f8"}
                  onChange={(value) => setTheme({ text: value })}
                />
              </div>
              <div className="flex flex-col gap-3 text-sm sm:max-w-sm">
                <span className="text-slate-400">Particle</span>
                <ParticleSelect
                  value={form.theme_config.particle ?? "sparkle"}
                  onChange={(particle) => setTheme({ particle })}
                />
              </div>
            </section>

            <section className="glass space-y-4 p-5 sm:p-6">
              <h2 className="font-sans text-sm font-semibold tracking-wide text-slate-200 uppercase">
                Палитра 3D-коробки
              </h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {(
                  [
                    ["body", "Body"],
                    ["bodyDark", "Body dark"],
                    ["lid", "Lid"],
                    ["lidLight", "Lid light"],
                    ["ribbon", "Ribbon"],
                    ["ribbonDark", "Ribbon dark"],
                  ] as const
                ).map(([key, label]) => (
                  <ColorSwatch
                    key={key}
                    label={label}
                    value={gift[key]}
                    onChange={(value) => setGiftBox(key, value)}
                  />
                ))}
              </div>
            </section>
          </div>

          <aside className="space-y-4 lg:sticky lg:top-20 lg:self-start">
            <div>
              <p className="mb-2 text-xs font-semibold tracking-wide text-slate-400 uppercase">
                Карточка на лендинге
              </p>
              <article
                className="design-banner"
                style={{ background: gradientCss(bannerTheme.gradient) }}
              >
                {hasPreviewImage ? (
                  <>
                    <img
                      src={bannerCover}
                      alt=""
                      className="design-banner__image"
                      style={{ objectPosition: DEFAULT_COVER_POSITION }}
                      onError={(event) => {
                        event.currentTarget.style.display = "none";
                      }}
                    />
                    <div className="design-banner__blur" aria-hidden>
                      <img
                        src={bannerCover}
                        alt=""
                        className="design-banner__blur-image"
                        style={{ objectPosition: DEFAULT_COVER_POSITION }}
                        onError={(event) => {
                          event.currentTarget.style.display = "none";
                        }}
                      />
                    </div>
                  </>
                ) : null}
                <div className="design-banner__scrim" />
                <div className="design-banner__content">
                  <h3 className="design-banner__title">
                    {previewDesign.name || "Название темы"}
                  </h3>
                  {previewDesign.description ? (
                    <p className="design-banner__pill">{previewDesign.description}</p>
                  ) : (
                    <p className="design-banner__pill opacity-70">
                      Описание появится здесь
                    </p>
                  )}
                  <span className="design-banner__cta">Собрать в этой теме</span>
                </div>
              </article>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold tracking-wide text-slate-400 uppercase">
                Открытие бокса
              </p>
              <div className="glass overflow-hidden !rounded-xl" style={{ height: 480 }}>
                <DesignGiftPreview design={previewDesign} />
              </div>
            </div>
          </aside>
        </div>
      </div>
    </PageTransition>
  );
}
