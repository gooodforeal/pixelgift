import type {
  AdminBoxDesign,
  Box,
  BoxAssistantChatPayload,
  BoxAssistantChatResult,
  BoxAssistantHistoryResult,
  BoxDesign,
  BoxItemType,
  BoxPayload,
  Cart,
  CheckoutResult,
  CurrentUser,
  DesignAssetUpload,
  DesignRating,
  MediaFile,
  PaginatedBalanceLogs,
  PaginatedBoxes,
  PaginatedOrders,
  PaginatedPromoCodes,
  PaginatedSupportTickets,
  Product,
  PromoCode,
  PublicBox,
  SupportTicket,
  SupportTicketStatus,
  TelegramLoginStart,
  TelegramLoginStatus,
  ThemeConfig,
  UnlockPublicBoxResult,
  UserProductBalance,
} from "./types";
import { isAuthed, setAuthed } from "./auth";

export interface OpenedThisMonthStats {
  count: number;
  period_start: string;
  period_end: string;
  timezone: string;
}

export const API_URL = import.meta.env.VITE_API_URL ?? "/api";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

let refreshInFlight: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      try {
        const response = await fetch(`${API_URL}/auth/refresh`, {
          method: "POST",
          credentials: "include",
        });
        if (!response.ok) {
          setAuthed(false);
          return false;
        }
        setAuthed(true);
        return true;
      } catch {
        setAuthed(false);
        return false;
      } finally {
        refreshInFlight = null;
      }
    })();
  }
  return refreshInFlight;
}

/** Restore session from HttpOnly cookies (access or refresh). */
export async function bootstrapAuth(): Promise<boolean> {
  try {
    const me = await fetch(`${API_URL}/auth/me`, { credentials: "include" });
    if (me.ok) {
      setAuthed(true);
      return true;
    }
  } catch {
    /* ignore and try refresh */
  }

  return refreshAccessToken();
}

async function request<T>(
  path: string,
  init: RequestInit = {},
  options: { retryOnUnauthorized?: boolean } = {},
): Promise<T> {
  const { retryOnUnauthorized = true } = options;
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (response.status === 401 && retryOnUnauthorized && path !== "/auth/refresh") {
    const ok = await refreshAccessToken();
    if (ok) {
      return request<T>(path, init, { retryOnUnauthorized: false });
    }
  }

  if (!response.ok) {
    throw new ApiError(response.status, await readError(response));
  }

  if (response.status === 204) return undefined as T;
  const data = (await response.json()) as { result?: T };
  return data.result as T;
}

async function readError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as {
      message?: unknown;
      detail?: unknown;
    };
    if (typeof data.message === "string" && data.message) return data.message;
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      const first = data.detail[0] as { msg?: string } | undefined;
      if (first?.msg) return first.msg;
    }
  } catch {
    /* body is not json */
  }
  return `Ошибка запроса (${response.status})`;
}

export const api = {
  startLogin: () =>
    request<TelegramLoginStart>("/auth/telegram/start", { method: "POST" }),

  loginStatus: (code: string) =>
    request<TelegramLoginStatus>(`/auth/telegram/status?code=${encodeURIComponent(code)}`),

  refresh: () => refreshAccessToken(),

  logout: () =>
    request<void>("/auth/logout", { method: "POST" }, { retryOnUnauthorized: false }),

  me: () => request<CurrentUser>("/auth/me"),

  openedThisMonth: () => request<OpenedThisMonthStats>("/boxes/opens"),

  updateMe: (payload: { notifications_enabled: boolean }) =>
    request<CurrentUser>("/auth/me", {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  designs: () => request<BoxDesign[]>("/designs"),

  rateDesign: (designId: string, stars: number) =>
    request<DesignRating>(`/designs/${designId}/rating`, {
      method: "PUT",
      body: JSON.stringify({ stars }),
    }),

  adminDesigns: () => request<AdminBoxDesign[]>("/admin/designs"),

  adminDesign: (designId: string) =>
    request<AdminBoxDesign>(`/admin/designs/${designId}`),

  createAdminDesign: (payload: AdminDesignPayload) =>
    request<AdminBoxDesign>("/admin/designs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateAdminDesign: (designId: string, payload: AdminDesignPayload) =>
    request<AdminBoxDesign>(`/admin/designs/${designId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  patchAdminDesign: (
    designId: string,
    payload: Partial<AdminDesignPayload> & { is_active?: boolean },
  ) =>
    request<AdminBoxDesign>(`/admin/designs/${designId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  uploadDesignAsset: async (file: File) => {
    const body = new FormData();
    body.append("file", file);
    const asset = await request<DesignAssetUpload>("/admin/designs/upload", {
      method: "POST",
      body,
    });
    return { ...asset, url: toProxiedAssetUrl(asset.url) };
  },

  boxes: (params?: { page?: number; pageSize?: number }) => {
    const search = new URLSearchParams();
    if (params?.page != null) search.set("page", String(params.page));
    if (params?.pageSize != null) search.set("page_size", String(params.pageSize));
    const query = search.toString();
    return request<PaginatedBoxes>(`/boxes${query ? `?${query}` : ""}`);
  },

  box: (boxId: string) => request<Box>(`/boxes/${boxId}`),

  boxAssistantChat: (payload: BoxAssistantChatPayload) =>
    request<BoxAssistantChatResult>("/assistant/box-editor", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  boxAssistantHistory: (params?: {
    boxId?: string | null;
    threadId?: string | null;
  }) => {
    const search = new URLSearchParams();
    if (params?.boxId) search.set("box_id", params.boxId);
    if (params?.threadId) search.set("thread_id", params.threadId);
    const query = search.toString();
    return request<BoxAssistantHistoryResult>(
      `/assistant/box-editor/history${query ? `?${query}` : ""}`,
    );
  },

  downloadGiftCertificate: async (
    boxId: string,
    theme: "dark" | "light" = "dark",
  ) => {
    const path = `/boxes/${boxId}/certificate.pdf?theme=${theme}`;
    const doFetch = () =>
      fetch(`${API_URL}${path}`, { credentials: "include" });

    let response = await doFetch();
    if (response.status === 401) {
      const ok = await refreshAccessToken();
      if (ok) response = await doFetch();
    }
    if (!response.ok) {
      throw new ApiError(response.status, await readError(response));
    }
    const blob = await response.blob();
    const disposition = response.headers.get("Content-Disposition") ?? "";
    const match = /filename="([^"]+)"/.exec(disposition);
    const filename = match?.[1] ?? `pixelgift-${boxId}-${theme}.pdf`;
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  },

  createBox: (payload: BoxPayload) =>
    request<Box>("/boxes", { method: "POST", body: JSON.stringify(payload) }),

  updateBox: (boxId: string, payload: BoxPayload) =>
    request<Box>(`/boxes/${boxId}`, { method: "PUT", body: JSON.stringify(payload) }),

  publishBox: (boxId: string) =>
    request<Box>(`/boxes/${boxId}/publish`, { method: "POST" }),

  archiveBox: (boxId: string) =>
    request<Box>(`/boxes/${boxId}/archive`, { method: "POST" }),

  unarchiveBox: (boxId: string) =>
    request<Box>(`/boxes/${boxId}/unarchive`, { method: "POST" }),

  uploadMedia: (file: File, kind?: BoxItemType) => {
    const body = new FormData();
    body.append("file", file);
    if (kind) body.append("kind", kind);
    return request<MediaFile>("/media", { method: "POST", body });
  },

  addItem: (
    boxId: string,
    mediaFileId: string,
    caption?: string | null,
    itemType?: "drawing" | "circle",
    metadata?: Record<string, unknown>,
  ) =>
    request<Box>(`/boxes/${boxId}/items`, {
      method: "POST",
      body: JSON.stringify({
        media_file_id: mediaFileId,
        caption: caption ?? null,
        item_type: itemType ?? null,
        ...(metadata && Object.keys(metadata).length > 0
          ? { metadata }
          : {}),
      }),
    }),

  addTextItem: (boxId: string, text: string) =>
    request<Box>(`/boxes/${boxId}/items`, {
      method: "POST",
      body: JSON.stringify({ item_type: "text", caption: text }),
    }),

  addToyItem: (boxId: string, toyCode: string, caption?: string | null) =>
    request<Box>(`/boxes/${boxId}/items`, {
      method: "POST",
      body: JSON.stringify({
        item_type: "toy",
        caption: caption?.trim() || null,
        metadata: { toy_code: toyCode },
      }),
    }),

  addGeopointItem: (
    boxId: string,
    coords: { lat: number; lng: number },
    caption?: string | null,
  ) =>
    request<Box>(`/boxes/${boxId}/items`, {
      method: "POST",
      body: JSON.stringify({
        item_type: "geopoint",
        caption: caption?.trim() || null,
        metadata: {
          lat: coords.lat,
          lng: coords.lng,
        },
      }),
    }),

  addQuestionItem: (
    boxId: string,
    payload: {
      question: string;
      options: string[];
      correct_index: number;
    },
    caption?: string | null,
  ) =>
    request<Box>(`/boxes/${boxId}/items`, {
      method: "POST",
      body: JSON.stringify({
        item_type: "question",
        caption: caption?.trim() || null,
        metadata: {
          question: payload.question,
          options: payload.options,
          correct_index: payload.correct_index,
        },
      }),
    }),

  updateItem: (
    boxId: string,
    itemId: string,
    caption: string | null,
    metadata?: Record<string, unknown>,
  ) =>
    request<Box>(`/boxes/${boxId}/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify({
        caption,
        ...(metadata !== undefined ? { metadata } : {}),
      }),
    }),

  removeItem: (boxId: string, itemId: string) =>
    request<Box>(`/boxes/${boxId}/items/${itemId}`, { method: "DELETE" }),

  reorderItems: (boxId: string, itemIds: string[]) =>
    request<Box>(`/boxes/${boxId}/items/reorder`, {
      method: "PUT",
      body: JSON.stringify({ item_ids: itemIds }),
    }),

  publicBox: (slug: string, unlockToken?: string | null) => {
    const search = new URLSearchParams();
    if (unlockToken) search.set("unlock_token", unlockToken);
    const query = search.toString();
    return request<PublicBox>(
      `/b/${encodeURIComponent(slug)}${query ? `?${query}` : ""}`,
    );
  },

  unlockPublicBox: (slug: string, password: string) =>
    request<UnlockPublicBoxResult>(`/b/${encodeURIComponent(slug)}/unlock`, {
      method: "POST",
      body: JSON.stringify({ password }),
    }),

  createSupportTicket: (payload: {
    contact: string;
    subject: string;
    description: string;
    files: File[];
  }) => {
    const body = new FormData();
    body.append("contact", payload.contact);
    body.append("subject", payload.subject);
    body.append("description", payload.description);
    for (const file of payload.files) {
      body.append("files", file);
    }
    return request<SupportTicket>("/support", { method: "POST", body });
  },

  supportConfig: () =>
    request<{ telegram_url: string }>("/support/config"),

  adminSupportTickets: (params?: {
    status?: SupportTicketStatus | null;
    sort?: "asc" | "desc";
    page?: number;
    pageSize?: number;
  }) => {
    const search = new URLSearchParams();
    if (params?.status) search.set("status", params.status);
    if (params?.sort) search.set("sort", params.sort);
    if (params?.page != null) search.set("page", String(params.page));
    if (params?.pageSize != null) search.set("page_size", String(params.pageSize));
    const query = search.toString();
    return request<PaginatedSupportTickets>(
      `/admin/support${query ? `?${query}` : ""}`,
    );
  },

  patchSupportTicketStatus: (ticketId: string, status: SupportTicketStatus) =>
    request<SupportTicket>(`/admin/support/${ticketId}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),

  products: () => request<Product[]>("/products"),

  cart: () => request<Cart>("/cart"),

  addCartItem: (payload: { sku: string; quantity: number }) =>
    request<Cart>("/cart/items", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateCartItem: (productId: string, quantity: number) =>
    request<Cart>(`/cart/items/${productId}`, {
      method: "PATCH",
      body: JSON.stringify({ quantity }),
    }),

  removeCartItem: (productId: string) =>
    request<Cart>(`/cart/items/${productId}`, { method: "DELETE" }),

  checkoutCart: (payload?: { promo_code?: string | null }) =>
    request<CheckoutResult>("/cart/checkout", {
      method: "POST",
      body: JSON.stringify(payload ?? {}),
    }),

  adminPromoCodes: (params?: { page?: number; pageSize?: number }) => {
    const search = new URLSearchParams();
    if (params?.page != null) search.set("page", String(params.page));
    if (params?.pageSize != null) search.set("page_size", String(params.pageSize));
    const query = search.toString();
    return request<PaginatedPromoCodes>(
      `/admin/promo-codes${query ? `?${query}` : ""}`,
    );
  },

  createAdminPromoCode: (payload: {
    code: string;
    discount_percent: number;
    expires_at: string;
    max_usages?: number | null;
  }) =>
    request<PromoCode>("/admin/promo-codes", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  setAdminPromoCodeActive: (promoId: string, isActive: boolean) =>
    request<PromoCode>(`/admin/promo-codes/${promoId}`, {
      method: "PATCH",
      body: JSON.stringify({ is_active: isActive }),
    }),

  adminProducts: () => request<Product[]>("/admin/products"),

  createAdminProduct: (payload: {
    sku: string;
    name: string;
    description?: string;
    unit_price: number;
    kind?: string;
    currency?: string;
    is_active?: boolean;
    image_urls?: string[];
    sale_discount_percent?: number | null;
  }) =>
    request<Product>("/admin/products", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateAdminProduct: (
    productId: string,
    payload: {
      name?: string;
      description?: string;
      unit_price?: number;
      is_active?: boolean;
      image_urls?: string[];
      sale_discount_percent?: number | null;
    },
  ) =>
    request<Product>(`/admin/products/${productId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  syncPendingOrders: () =>
    request<{ synced: number }>("/orders/sync", { method: "POST" }),

  orders: (params?: { page?: number; pageSize?: number }) => {
    const search = new URLSearchParams();
    if (params?.page != null) search.set("page", String(params.page));
    if (params?.pageSize != null) search.set("page_size", String(params.pageSize));
    const query = search.toString();
    return request<PaginatedOrders>(`/orders${query ? `?${query}` : ""}`);
  },

  balances: () => request<UserProductBalance[]>("/balances"),

  balanceLogs: (params?: { page?: number; pageSize?: number }) => {
    const search = new URLSearchParams();
    if (params?.page != null) search.set("page", String(params.page));
    if (params?.pageSize != null) search.set("page_size", String(params.pageSize));
    const query = search.toString();
    return request<PaginatedBalanceLogs>(
      `/balance-logs${query ? `?${query}` : ""}`,
    );
  },
};

/** Owner-side media URL — auth via HttpOnly access cookie (same-origin). */
export function ownMediaUrl(mediaFileId: string): string {
  return `${API_URL}/media/${mediaFileId}/content`;
}

export function supportAttachmentUrl(ticketId: string, attachmentId: string): string {
  return `${API_URL}/admin/support/${ticketId}/attachments/${attachmentId}/content`;
}

/** Public media URL for an unlocked box — no authentication needed. */
export function publicMediaUrl(
  slug: string,
  itemId: string,
  unlockToken?: string | null,
): string {
  const search = new URLSearchParams();
  if (unlockToken) search.set("unlock_token", unlockToken);
  const query = search.toString();
  return `${API_URL}/b/${encodeURIComponent(slug)}/items/${itemId}/content${
    query ? `?${query}` : ""
  }`;
}

/** Prefer same-origin /api proxy for design assets returned with absolute api_base_url. */
export function toProxiedAssetUrl(url: string): string {
  try {
    const parsed = new URL(url, window.location.origin);
    if (parsed.pathname.startsWith("/designs/assets/")) {
      const base = API_URL.startsWith("http")
        ? API_URL.replace(/\/$/, "")
        : `${window.location.origin}${API_URL.startsWith("/") ? "" : "/"}${API_URL}`.replace(
            /\/$/,
            "",
          );
      return `${base}${parsed.pathname}`;
    }
  } catch {
    /* keep original */
  }
  return url;
}

export type AdminDesignPayload = {
  code: string;
  name: string;
  preview_image_url: string;
  description: string | null;
  theme_config: ThemeConfig;
  is_active: boolean;
  sort_order: number;
};

export { isAuthed };
