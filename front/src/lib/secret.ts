import type { BoxItem, BoxItemType } from "./types";

const SECRET_PHOTO_TYPES: ReadonlySet<BoxItemType> = new Set(["image"]);

export function isSecretPhotoType(type: BoxItemType): boolean {
  return SECRET_PHOTO_TYPES.has(type);
}

export function secretFromMetadata(
  metadata: Record<string, unknown> | null | undefined,
): boolean {
  return metadata?.secret === true;
}

export function isSecretPhotoItem(item: Pick<BoxItem, "item_type" | "metadata">): boolean {
  return isSecretPhotoType(item.item_type) && secretFromMetadata(item.metadata);
}

export function withSecretMetadata(
  metadata: Record<string, unknown> | null | undefined,
  secret: boolean,
): Record<string, unknown> {
  const next = { ...(metadata ?? {}) };
  if (secret) {
    next.secret = true;
  } else {
    delete next.secret;
  }
  return next;
}
