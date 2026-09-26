import { useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Eye,
  EyeOff,
  ImagePlus,
  Images,
  Package,
  Pencil,
  Plus,
  X,
} from "lucide-react";

import { CardActionsMenu } from "../components/CardActionsMenu";
import { Modal } from "../components/Modal";
import { PageTransition } from "../components/PageTransition";
import { Spinner } from "../components/Spinner";
import { useToast } from "../components/Toast";
import { ApiError, api, toProxiedAssetUrl } from "../lib/api";
import { pluralize } from "../lib/format";
import type { Product } from "../lib/types";

const MAX_IMAGES = 5;

function formatPrice(kopecks: number, currency: string): string {
  const value = kopecks / 100;
  try {
    return new Intl.NumberFormat("ru-RU", {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(value);
  } catch {
    return `${value} ${currency}`;
  }
}

const FIELD =
  "mt-1.5 w-full rounded-xl border border-white/10 bg-ink-900/60 px-3 py-2 text-sm text-slate-100 outline-none focus:border-glow-cyan/50";

type ProductForm = {
  sku: string;
  name: string;
  description: string;
  priceRub: string;
  imageUrls: string[];
};

const emptyCreateForm = (): ProductForm => ({
  sku: "",
  name: "",
  description: "",
  priceRub: "99",
  imageUrls: [],
});

type ModalState =
  | { mode: "create"; form: ProductForm }
  | { mode: "edit"; productId: string; form: ProductForm }
  | null;

function ImageUrlsEditor({
  urls,
  disabled,
  uploading,
  onChange,
  onUpload,
}: {
  urls: string[];
  disabled?: boolean;
  uploading?: boolean;
  onChange: (urls: string[]) => void;
  onUpload: (file: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  return (
    <div className="sm:col-span-2">
      <p className="text-sm text-slate-400">
        Фото{" "}
        <span className="text-slate-500">
          ({urls.length}/{MAX_IMAGES})
        </span>
      </p>
      <div className="mt-2 flex flex-wrap gap-2">
        {urls.map((url) => (
          <div
            key={url}
            className="relative size-20 overflow-hidden rounded-xl border border-white/10"
          >
            <img
              src={toProxiedAssetUrl(url)}
              alt=""
              className="h-full w-full object-cover"
            />
            <button
              type="button"
              className="absolute top-1 right-1 grid size-6 place-items-center rounded-full bg-ink-950/80 text-slate-200"
              aria-label="Удалить фото"
              disabled={disabled}
              onClick={() => onChange(urls.filter((u) => u !== url))}
            >
              <X className="size-3.5" />
            </button>
          </div>
        ))}
        {urls.length < MAX_IMAGES ? (
          <button
            type="button"
            className="flex size-20 flex-col items-center justify-center gap-1 rounded-xl border border-dashed border-white/15 text-slate-400 transition hover:border-glow-cyan/40 hover:text-slate-200 disabled:opacity-50"
            disabled={disabled || uploading}
            onClick={() => inputRef.current?.click()}
          >
            <ImagePlus className="size-5" />
            <span className="text-[10px]">
              {uploading ? "…" : "Добавить"}
            </span>
          </button>
        ) : null}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          e.target.value = "";
          if (file) onUpload(file);
        }}
      />
    </div>
  );
}

export function AdminProductsPage() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [modal, setModal] = useState<ModalState>(null);
  const [uploading, setUploading] = useState(false);

  const productsQuery = useQuery({
    queryKey: ["admin-products"],
    queryFn: api.adminProducts,
  });

  const closeModal = () => setModal(null);

  const createMutation = useMutation({
    mutationFn: (form: ProductForm) => {
      const rubles = Number(form.priceRub.replace(",", "."));
      if (!Number.isFinite(rubles) || rubles < 0) {
        throw new Error("Укажите корректную цену");
      }
      return api.createAdminProduct({
        sku: form.sku.trim().toLowerCase(),
        name: form.name.trim(),
        description: form.description.trim(),
        unit_price: Math.round(rubles * 100),
        kind: "credit",
        currency: "RUB",
        is_active: true,
        image_urls: form.imageUrls,
      });
    },
    onSuccess: (product) => {
      void queryClient.invalidateQueries({ queryKey: ["admin-products"] });
      void queryClient.invalidateQueries({ queryKey: ["products"] });
      closeModal();
      toast(`Товар «${product.name}» создан`, "success");
    },
    onError: (error) => {
      toast((error as ApiError).message ?? "Не удалось создать", "error");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: {
        name?: string;
        description?: string;
        unit_price?: number;
        is_active?: boolean;
        image_urls?: string[];
      };
    }) => api.updateAdminProduct(id, payload),
    onSuccess: (_product, variables) => {
      void queryClient.invalidateQueries({ queryKey: ["admin-products"] });
      void queryClient.invalidateQueries({ queryKey: ["products"] });
      if (variables.payload.is_active === undefined) {
        closeModal();
        toast("Товар обновлён", "success");
      } else {
        toast(
          variables.payload.is_active ? "Товар активен" : "Товар скрыт",
          "success",
        );
      }
    },
    onError: (error) => {
      toast((error as ApiError).message ?? "Не удалось сохранить", "error");
    },
  });

  const products = productsQuery.data ?? [];
  const form = modal?.form;
  const canSubmit = useMemo(() => {
    if (!form) return false;
    const rubles = Number(form.priceRub.replace(",", "."));
    const pending = createMutation.isPending || updateMutation.isPending;
    if (modal?.mode === "create") {
      return (
        form.sku.trim().length >= 1 &&
        form.name.trim().length >= 1 &&
        Number.isFinite(rubles) &&
        rubles >= 0 &&
        !pending
      );
    }
    return (
      form.name.trim().length >= 1 &&
      Number.isFinite(rubles) &&
      rubles >= 0 &&
      !pending
    );
  }, [form, modal?.mode, createMutation.isPending, updateMutation.isPending]);

  const patchForm = (patch: Partial<ProductForm>) => {
    setModal((current) =>
      current ? { ...current, form: { ...current.form, ...patch } } : current,
    );
  };

  const uploadImage = async (file: File) => {
    if (!modal || modal.form.imageUrls.length >= MAX_IMAGES) return;
    setUploading(true);
    try {
      const asset = await api.uploadDesignAsset(file);
      setModal((current) => {
        if (!current || current.form.imageUrls.length >= MAX_IMAGES) {
          return current;
        }
        return {
          ...current,
          form: {
            ...current.form,
            imageUrls: [...current.form.imageUrls, asset.url],
          },
        };
      });
    } catch (error) {
      toast((error as ApiError).message ?? "Не удалось загрузить фото", "error");
    } finally {
      setUploading(false);
    }
  };

  if (productsQuery.isPending) {
    return <Spinner label="Загружаем товары…" className="py-32" />;
  }

  if (productsQuery.isError) {
    return (
      <PageTransition>
        <div className="glass-soft mt-16 p-8 text-center text-sm text-rose-200">
          {(productsQuery.error as Error).message}
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="pt-10 pb-10 sm:pt-14">
        <Link
          to="/app/panel"
          className="btn-ghost inline-flex items-center gap-2 px-3 py-2 text-sm"
        >
          <ArrowLeft className="size-4" />
          К панели
        </Link>

        <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="chip w-fit">
              <Package className="size-3.5" />
              Панель
            </p>
            <h1 className="mt-3 font-sans text-2xl font-semibold tracking-tight sm:text-3xl">
              Товары
            </h1>
            <p className="mt-2 max-w-xl text-sm text-slate-400">
              Название, описание, до {MAX_IMAGES} фото, цена и активность.
            </p>
          </div>
          <button
            type="button"
            className="btn-primary"
            onClick={() =>
              setModal({ mode: "create", form: emptyCreateForm() })
            }
          >
            <Plus className="size-4" />
            Новый товар
          </button>
        </div>

        <section className="mt-8">
          {!products.length ? (
            <p className="text-sm text-slate-400">Пока нет товаров.</p>
          ) : (
            <div className="boxes-list flex flex-col gap-2.5">
              {products.map((product: Product, index) => {
                const cover = product.image_urls?.[0];
                const photoCount = product.image_urls?.length ?? 0;
                return (
                  <motion.article
                    key={product.id}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: Math.min(index, 10) * 0.03 }}
                    className="boxes-list__row glass relative flex items-center gap-3 !rounded-xl p-2.5 sm:gap-4 sm:p-3"
                  >
                    <div className="boxes-list__cover shrink-0 overflow-hidden rounded-lg">
                      {cover ? (
                        <img
                          src={toProxiedAssetUrl(cover)}
                          alt=""
                          className="h-[4.5rem] w-[4.5rem] object-cover sm:h-16 sm:w-28"
                        />
                      ) : (
                        <div className="grid h-[4.5rem] w-[4.5rem] place-items-center bg-gradient-to-br from-glow-cyan/10 via-transparent to-glow-violet/10 sm:h-16 sm:w-28">
                          <Package
                            className="size-7 text-slate-500/80"
                            strokeWidth={1.5}
                          />
                        </div>
                      )}
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="truncate font-sans text-sm font-semibold sm:text-base">
                          {product.name}
                        </h2>
                        <span
                          className={`status-badge ${
                            product.is_active
                              ? "status-badge--active"
                              : "status-badge--archived"
                          }`}
                        >
                          {product.is_active ? (
                            <Eye className="status-badge__icon" strokeWidth={2.25} />
                          ) : (
                            <EyeOff
                              className="status-badge__icon"
                              strokeWidth={2.25}
                            />
                          )}
                          <span>{product.is_active ? "Активен" : "Скрыт"}</span>
                        </span>
                      </div>
                      <p className="mt-1 truncate text-xs text-slate-400 sm:text-sm">
                        <span className="font-mono">{product.sku}</span>
                        {" · "}
                        {formatPrice(product.unit_price, product.currency)}
                        {product.description
                          ? ` · ${product.description}`
                          : ""}
                      </p>
                    </div>

                    <div className="hidden items-center gap-2 md:flex">
                      <span className="chip px-2 py-0.5">
                        <Images className="size-3.5" />
                        {photoCount}{" "}
                        {pluralize(photoCount, ["фото", "фото", "фото"])}
                      </span>
                    </div>

                    <div className="flex shrink-0 items-center gap-1">
                      <CardActionsMenu
                        label={`Действия с товаром «${product.name}»`}
                        items={[
                          {
                            key: "edit",
                            label: "Изменить",
                            icon: <Pencil className="size-3.5" />,
                            onClick: () =>
                              setModal({
                                mode: "edit",
                                productId: product.id,
                                form: {
                                  sku: product.sku,
                                  name: product.name,
                                  description: product.description ?? "",
                                  priceRub: String(product.unit_price / 100),
                                  imageUrls: [...(product.image_urls ?? [])],
                                },
                              }),
                          },
                          {
                            key: "toggle",
                            label: product.is_active ? "Скрыть" : "Показать",
                            icon: product.is_active ? (
                              <EyeOff className="size-3.5" />
                            ) : (
                              <Eye className="size-3.5" />
                            ),
                            disabled: updateMutation.isPending,
                            onClick: () =>
                              updateMutation.mutate({
                                id: product.id,
                                payload: { is_active: !product.is_active },
                              }),
                          },
                        ]}
                      />
                    </div>
                  </motion.article>
                );
              })}
            </div>
          )}
        </section>
      </div>

      <Modal
        open={modal != null}
        title={modal?.mode === "edit" ? "Изменить товар" : "Новый товар"}
        description={
          modal?.mode === "edit"
            ? `SKU: ${modal.form.sku}`
            : "SKU после создания изменить нельзя."
        }
        onClose={closeModal}
        size="lg"
        footer={
          <>
            <button type="button" className="btn-ghost" onClick={closeModal}>
              Отмена
            </button>
            <button
              type="submit"
              form="admin-product-form"
              className="btn-primary"
              disabled={!canSubmit || uploading}
            >
              {modal?.mode === "edit" ? "Сохранить" : "Создать"}
            </button>
          </>
        }
      >
        {form ? (
          <form
            id="admin-product-form"
            className="grid gap-4 sm:grid-cols-2"
            onSubmit={(e) => {
              e.preventDefault();
              if (!modal || !canSubmit) return;
              if (modal.mode === "create") {
                createMutation.mutate(modal.form);
                return;
              }
              const rubles = Number(modal.form.priceRub.replace(",", "."));
              if (!Number.isFinite(rubles) || rubles < 0) {
                toast("Укажите корректную цену", "error");
                return;
              }
              updateMutation.mutate({
                id: modal.productId,
                payload: {
                  name: modal.form.name.trim(),
                  description: modal.form.description.trim(),
                  unit_price: Math.round(rubles * 100),
                  image_urls: modal.form.imageUrls,
                },
              });
            }}
          >
            {modal?.mode === "create" ? (
              <label className="block text-sm text-slate-400">
                SKU
                <input
                  type="text"
                  value={form.sku}
                  onChange={(e) =>
                    patchForm({ sku: e.target.value.toLowerCase() })
                  }
                  maxLength={64}
                  placeholder="box_credit"
                  className={`${FIELD} font-mono`}
                  autoComplete="off"
                  spellCheck={false}
                  autoFocus
                />
              </label>
            ) : null}
            <label
              className={`block text-sm text-slate-400 ${
                modal?.mode === "edit" ? "sm:col-span-2" : ""
              }`}
            >
              Название
              <input
                type="text"
                value={form.name}
                onChange={(e) => patchForm({ name: e.target.value })}
                maxLength={128}
                placeholder="Бокс"
                className={FIELD}
                autoFocus={modal?.mode === "edit"}
              />
            </label>
            <label className="block text-sm text-slate-400 sm:col-span-2">
              Описание
              <textarea
                value={form.description}
                onChange={(e) => patchForm({ description: e.target.value })}
                maxLength={2000}
                rows={3}
                placeholder="Что получает покупатель"
                className={`${FIELD} resize-y`}
              />
            </label>
            <ImageUrlsEditor
              urls={form.imageUrls}
              disabled={createMutation.isPending || updateMutation.isPending}
              uploading={uploading}
              onChange={(imageUrls) => patchForm({ imageUrls })}
              onUpload={(file) => void uploadImage(file)}
            />
            <label className="block text-sm text-slate-400">
              Цена, ₽
              <input
                type="number"
                min={0}
                step={1}
                value={form.priceRub}
                onChange={(e) => patchForm({ priceRub: e.target.value })}
                className={FIELD}
              />
            </label>
          </form>
        ) : null}
      </Modal>
    </PageTransition>
  );
}
