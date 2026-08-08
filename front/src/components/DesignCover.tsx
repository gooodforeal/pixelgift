import type { ReactNode } from "react";

import { toProxiedAssetUrl } from "../lib/api";
import { gradientCss, resolveTheme } from "../lib/theme";
import type { ThemeConfig } from "../lib/types";

/** Resolve cover URL from design.preview_image_url (API /designs/assets/{id}). */
export function designCoverUrl(
  design:
    | { preview_image_url?: string | null }
    | string
    | null
    | undefined,
): string {
  if (!design || typeof design === "string") {
    return "";
  }
  const preview = design.preview_image_url;
  if (!preview) {
    return "";
  }
  return toProxiedAssetUrl(preview);
}

interface DesignCoverProps {
  code: string;
  previewImageUrl?: string | null;
  themeConfig?: ThemeConfig | null;
  className?: string;
  heightClassName?: string;
  children?: ReactNode;
}

export function DesignCover({
  code: _code,
  previewImageUrl = null,
  themeConfig = null,
  className = "",
  heightClassName = "h-36",
  children,
}: DesignCoverProps) {
  const theme = resolveTheme(themeConfig);
  const objectPosition = theme.cover_object_position;
  const coverUrl = designCoverUrl({ preview_image_url: previewImageUrl });

  return (
    <div
      className={`design-cover relative w-full min-w-0 shrink-0 overflow-hidden ${heightClassName} ${className}`}
      style={{ background: gradientCss(theme.gradient) }}
    >
      {coverUrl ? (
        <div
          className="design-cover__media pointer-events-none absolute inset-0"
          style={{
            backgroundImage: `url(${coverUrl})`,
            backgroundSize: "cover",
            backgroundPosition: objectPosition,
            backgroundRepeat: "no-repeat",
          }}
          role="img"
          aria-hidden
        />
      ) : null}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-ink-950/55 via-ink-950/10 to-transparent" />
      {children}
    </div>
  );
}
