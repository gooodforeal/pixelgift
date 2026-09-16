export type BoxStatus = "draft" | "scheduled" | "active" | "opened" | "archived";

export type BoxItemType =
  | "image"
  | "drawing"
  | "gif"
  | "video"
  | "circle"
  | "voice"
  | "text"
  | "toy"
  | "geopoint";

export interface BoxItem {
  id: string;
  media_file_id: string | null;
  item_type: BoxItemType;
  sort_order: number;
  caption: string | null;
  metadata: Record<string, unknown>;
}

export interface Box {
  id: string;
  owner_id: string;
  design_id: string;
  public_slug: string;
  title: string;
  recipient_name: string;
  recipient_email: string | null;
  activates_at: string;
  status: BoxStatus;
  timezone: string;
  message: string | null;
  preview_title: string | null;
  preview_image_url: string | null;
  published_at: string | null;
  first_opened_at: string | null;
  items: BoxItem[];
}

export interface PaginatedBoxes {
  items: Box[];
  total: number;
  page: number;
  page_size: number;
  status_counts: Partial<Record<BoxStatus, number>>;
}

export interface PublicBox {
  public_slug: string;
  title: string;
  recipient_name: string;
  activates_at: string;
  status: BoxStatus;
  timezone: string;
  preview_title: string | null;
  preview_image_url: string | null;
  content_unlocked: boolean;
  message: string | null;
  design_code: string | null;
  theme_config: ThemeConfig;
  items: BoxItem[];
}

export interface ThemeConfig {
  gradient?: string[];
  accent?: string;
  text?: string;
  particle?:
    | "heart"
    | "confetti"
    | "snow"
    | "sparkle"
    | "petal"
    | "pixel"
    | "star"
    | "bubble"
    | "leaf"
    | "music"
    | "flame";
  cover_object_position?: string;
  background_image_url?: string | null;
  preview_image_url_light?: string | null;
  gift_box?: {
    body?: string;
    bodyDark?: string;
    lid?: string;
    lidLight?: string;
    ribbon?: string;
    ribbonDark?: string;
  };
}

export interface BoxDesign {
  id: string;
  code: string;
  name: string;
  preview_image_url: string;
  sort_order: number;
  description: string | null;
  theme_config: ThemeConfig;
  rating_avg: number;
  rating_count: number;
  my_rating: number | null;
}

export interface DesignRating {
  design_id: string;
  stars: number;
  rating_avg: number;
  rating_count: number;
}

export interface AdminBoxDesign extends BoxDesign {
  is_active: boolean;
}

export interface DesignAssetUpload {
  id: string;
  url: string;
  mime_type: string;
  size_bytes: number;
}

export interface MediaFile {
  id: string;
  owner_id: string;
  storage_key: string;
  mime_type: string;
  media_kind: BoxItemType;
  size_bytes: number;
  original_filename: string | null;
}

export interface TelegramLoginStart {
  code: string;
  bot_url: string;
  expires_at: string;
}

export interface TelegramLoginStatus {
  status: "pending" | "completed" | "consumed" | "expired";
  access_token: string | null;
  token_type: string | null;
  user_id: string | null;
}

export interface CurrentUser {
  id: string;
  first_name: string;
  last_name: string | null;
  username: string | null;
  language_code: string | null;
  photo_url: string | null;
  is_admin: boolean;
  created_at: string;
  last_seen_at: string | null;
}

export interface BoxPayload {
  design_id: string;
  title: string;
  recipient_name: string;
  recipient_email: string;
  activates_at: string;
  timezone: string;
  public_slug?: string | null;
  message?: string | null;
  preview_title?: string | null;
  preview_image_url?: string | null;
}
