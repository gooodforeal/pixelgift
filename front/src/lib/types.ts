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
  | "geopoint"
  | "question";

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
  unlock_password: string | null;
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
  password_required: boolean;
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
  preview_asset_id?: string | null;
  preview_asset_id_light?: string | null;
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
  notifications_enabled: boolean;
  created_at: string;
  last_seen_at: string | null;
}

export interface BoxPayload {
  design_id: string;
  title: string;
  recipient_name: string;
  recipient_email: string;
  unlock_password: string;
  activates_at: string;
  timezone: string;
  public_slug?: string | null;
  message?: string | null;
  preview_title?: string | null;
  preview_image_url?: string | null;
  assistant_thread_id?: string | null;
}

export interface UnlockPublicBoxResult {
  unlock_token: string | null;
  box: PublicBox;
}

export type SupportTicketStatus = "new" | "in_progress" | "resolved" | "closed";

export interface SupportTicketAttachment {
  id: string;
  mime_type: string;
  size_bytes: number;
  original_filename: string | null;
}

export interface SupportTicket {
  id: string;
  contact: string;
  subject: string;
  description: string;
  status: SupportTicketStatus;
  created_at: string;
  updated_at: string;
  attachments: SupportTicketAttachment[];
}

export interface PaginatedSupportTickets {
  items: SupportTicket[];
  total: number;
  page: number;
  page_size: number;
}

export interface Product {
  id: string;
  sku: string;
  name: string;
  description?: string;
  image_urls?: string[];
  kind: string;
  unit_price: number;
  currency: string;
  is_active: boolean;
  sale_discount_percent?: number | null;
  sale_unit_price?: number | null;
}

export interface CartItem {
  product_id: string;
  sku: string;
  name: string;
  unit_price: number;
  currency: string;
  quantity: number;
  amount: number;
  compare_at_price?: number | null;
  sale_discount_percent?: number | null;
}

export interface Cart {
  id: string;
  items: CartItem[];
  total_amount: number;
  currency: string;
}

export interface CheckoutResult {
  order_id: string;
  confirmation_url: string | null;
  amount: number;
  currency: string;
  discount_percent?: number | null;
  amount_before_discount?: number | null;
}

export type OrderStatus = "pending" | "succeeded" | "canceled";

export interface OrderItem {
  product_id: string;
  quantity: number;
  unit_price: number;
  amount: number;
}

export interface Order {
  id: string;
  status: OrderStatus;
  amount: number;
  currency: string;
  confirmation_url: string | null;
  paid_at: string | null;
  discount_percent?: number | null;
  amount_before_discount?: number | null;
  items: OrderItem[];
  created_at: string;
}

export interface PaginatedOrders {
  items: Order[];
  total: number;
  page: number;
  page_size: number;
}

export interface PromoCode {
  id: string;
  code: string;
  discount_percent: number;
  expires_at: string;
  usage_count: number;
  is_active: boolean;
  created_at: string;
}

export interface PaginatedPromoCodes {
  items: PromoCode[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserProductBalance {
  product_id: string;
  sku: string;
  name: string;
  balance: number;
}

export interface BalanceLog {
  id: string;
  product_id: string;
  sku: string;
  name: string;
  delta: number;
  balance_after: number;
  reason: string;
  reference_type: string;
  reference_id: string;
  created_at: string;
}

export interface PaginatedBalanceLogs {
  items: BalanceLog[];
  total: number;
  page: number;
  page_size: number;
}

export type BoxWizardAssistantStep =
  | "design"
  | "details"
  | "content"
  | "publish"
  | "certificate";

export interface AssistantHistoryMessage {
  role: "user" | "assistant";
  content: string;
}

export interface BoxEditorFormSnapshot {
  design_id?: string | null;
  title?: string | null;
  recipient_name?: string | null;
  recipient_email?: string | null;
  unlock_password_set?: boolean | null;
  activates_at?: string | null;
  timezone?: string | null;
  message?: string | null;
  preview_title?: string | null;
}

export interface BoxAssistantChatPayload {
  message: string;
  step: BoxWizardAssistantStep;
  thread_id?: string | null;
  box_id?: string | null;
  form?: BoxEditorFormSnapshot | null;
}

export interface BoxAssistantChatResult {
  reply: string;
  thread_id: string;
  context: Record<string, unknown>;
}

export interface BoxAssistantHistoryResult {
  thread_id: string;
  messages: AssistantHistoryMessage[];
}
