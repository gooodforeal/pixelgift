import type {
  AdminBoxDesign,
  Box,
  BoxDesign,
  BoxItemType,
  BoxPayload,
  CurrentUser,
  DesignAssetUpload,
  DesignRating,
  MediaFile,
  PublicBox,
  TelegramLoginStart,
  TelegramLoginStatus,
  ThemeConfig,
} from "./types";
import { isAuthed, setAuthed } from "./auth";

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
  return (await response.json()) as T;
}

async function readError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: unknown };
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

  boxes: () => request<Box[]>("/boxes"),

  box: (boxId: string) => request<Box>(`/boxes/${boxId}`),

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
    itemType?: "drawing",
  ) =>
    request<Box>(`/boxes/${boxId}/items`, {
      method: "POST",
      body: JSON.stringify({
        media_file_id: mediaFileId,
        caption: caption ?? null,
        item_type: itemType ?? null,
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

  updateItem: (boxId: string, itemId: string, caption: string | null) =>
    request<Box>(`/boxes/${boxId}/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify({ caption }),
    }),

  removeItem: (boxId: string, itemId: string) =>
    request<Box>(`/boxes/${boxId}/items/${itemId}`, { method: "DELETE" }),

  reorderItems: (boxId: string, itemIds: string[]) =>
    request<Box>(`/boxes/${boxId}/items/reorder`, {
      method: "PUT",
      body: JSON.stringify({ item_ids: itemIds }),
    }),

  publicBox: (slug: string) => request<PublicBox>(`/b/${encodeURIComponent(slug)}`),
};

/** Owner-side media URL — auth via HttpOnly access cookie (same-origin). */
export function ownMediaUrl(mediaFileId: string): string {
  return `${API_URL}/media/${mediaFileId}/content`;
}

/** Public media URL for an unlocked box — no authentication needed. */
export function publicMediaUrl(slug: string, itemId: string): string {
  return `${API_URL}/b/${encodeURIComponent(slug)}/items/${itemId}/content`;
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
