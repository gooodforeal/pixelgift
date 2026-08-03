import type { ReactNode } from "react";

import { gradientCss, resolveTheme } from "../lib/theme";
import type { BoxDesign, ThemeConfig } from "../lib/types";

/** Resolve cover URL: prefer API preview, fall back to local seed JPGs for CDN placeholders. */
const LEGACY_DESIGN_COVERS: Record<string, string> = {
  romantic: "romantic-night",
  birthday: "birthday-confetti",
  winter: "winter-magic",
  golden: "golden-anniversary",
  spring: "spring-bloom",
  retro: "retro-pixel",
};

export function designCoverUrl(
  design: Pick<BoxDesign, "code" | "preview_image_url"> | string,
): string {
  if (typeof design === "string") {
    const fileCode = LEGACY_DESIGN_COVERS[design] ?? design;
    return `/designs/${fileCode}.jpg`;
  }
  const preview = design.preview_image_url;
  if (preview && !preview.includes("cdn.pixelgift.app")) {
    return preview;
  }
  const fileCode = LEGACY_DESIGN_COVERS[design.code] ?? design.code;
  return `/designs/${fileCode}.jpg`;
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
  code,
  previewImageUrl = null,
  themeConfig = null,
  className = "",
  heightClassName = "h-36",
  children,
}: DesignCoverProps) {
  const theme = resolveTheme(themeConfig);
  const objectPosition = theme.cover_object_position;
  const coverUrl = designCoverUrl({
    code,
    preview_image_url: previewImageUrl ?? `https://cdn.pixelgift.app/designs/${code}.jpg`,
  });

  return (
    <div
      className={`design-cover relative w-full min-w-0 shrink-0 overflow-hidden ${heightClassName} ${className}`}
      style={{ background: gradientCss(theme.gradient) }}
    >
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
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-ink-950/55 via-ink-950/10 to-transparent" />
      {children}
    </div>
  );
}
