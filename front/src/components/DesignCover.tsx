import type { ReactNode } from "react";

import { toProxiedAssetUrl } from "../lib/api";
import { gradientCss, resolveTheme } from "../lib/theme";
import type { ThemeConfig } from "../lib/types";
import type { UiTheme } from "../lib/uiTheme";
import { useUiTheme } from "../hooks/useUiTheme";

type CoverSource = {
  preview_image_url?: string | null;
  theme_config?: ThemeConfig | null;
};

/** Resolve cover URL from design.preview_image_url (API /designs/assets/{id}). */
export function designCoverUrl(
  design: CoverSource | string | null | undefined,
  uiTheme: UiTheme = "dark",
): string {
  if (!design || typeof design === "string") {
    return "";
  }
  const lightUrl = design.theme_config?.preview_image_url_light;
  const preview =
    uiTheme === "light" && lightUrl
      ? lightUrl
      : design.preview_image_url;
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
  const { theme: uiTheme } = useUiTheme();
  const theme = resolveTheme(themeConfig);
  const objectPosition = theme.cover_object_position;
  const coverUrl = designCoverUrl(
    { preview_image_url: previewImageUrl, theme_config: themeConfig },
    uiTheme,
  );

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
      <div className="design-cover__scrim" />
      {children}
    </div>
  );
}
