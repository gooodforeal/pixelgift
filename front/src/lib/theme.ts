import type { BoxDesign, ThemeConfig } from "./types";

export const fallbackTheme: Required<
  Pick<ThemeConfig, "gradient" | "accent" | "text" | "cover_object_position">
> & {
  particle: NonNullable<ThemeConfig["particle"]>;
  background_image_url: string | null;
  gift_box: NonNullable<ThemeConfig["gift_box"]>;
} = {
  gradient: ["#0b0718", "#4c1d95", "#831843"],
  accent: "#a855f7",
  text: "#f5f3ff",
  particle: "sparkle",
  cover_object_position: "50% 50%",
  background_image_url: null,
  gift_box: {},
};

export function resolveTheme(design?: BoxDesign | ThemeConfig | null) {
  const config: ThemeConfig =
    design && "theme_config" in design ? design.theme_config : (design ?? {});
  const gradient =
    config.gradient && config.gradient.length >= 2 ? config.gradient : fallbackTheme.gradient;

  return {
    gradient,
    accent: config.accent ?? fallbackTheme.accent,
    text: config.text ?? fallbackTheme.text,
    particle: config.particle ?? fallbackTheme.particle,
    cover_object_position: config.cover_object_position ?? fallbackTheme.cover_object_position,
    background_image_url: config.background_image_url ?? null,
    gift_box: config.gift_box ?? {},
  };
}

export function gradientCss(gradient: string[], angle = 140): string {
  return `linear-gradient(${angle}deg, ${gradient.join(", ")})`;
}

export function radialGlowCss(accent: string): string {
  return `radial-gradient(circle at 50% 0%, ${accent}55, transparent 60%)`;
}

export function themeBackgroundLayers(
  theme: ReturnType<typeof resolveTheme>,
  angle = 165,
): { backgroundImage: string; backgroundSize: string; backgroundPosition: string } {
  const layers = [gradientCss(theme.gradient, angle)];
  if (theme.background_image_url) {
    layers.unshift(`url(${theme.background_image_url})`);
  }
  return {
    backgroundImage: layers.join(", "),
    backgroundSize: theme.background_image_url ? "cover, cover" : "cover",
    backgroundPosition: "center",
  };
}
