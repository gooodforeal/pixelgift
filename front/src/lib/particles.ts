import type { ThemeConfig } from "./types";

export type ParticleKind = NonNullable<ThemeConfig["particle"]>;

export const PARTICLE_GLYPHS: Record<ParticleKind, string[]> = {
  heart: ["♥", "❤", "♡"],
  confetti: ["▰", "●", "▲"],
  snow: ["❄", "❅", "✳"],
  sparkle: ["✦", "✧", "✶"],
  petal: ["❀", "✿", "❁"],
  pixel: ["▪", "▫", "▮"],
  star: ["★", "☆", "✦"],
  bubble: ["○", "◦", "●"],
  leaf: ["❦", "❧", "☘"],
  music: ["♪", "♫", "♬"],
  flame: ["▴", "✦", "✧"],
};

export const PARTICLE_OPTIONS: {
  value: ParticleKind;
  label: string;
  glyph: string;
}[] = (
  [
    "heart",
    "confetti",
    "snow",
    "sparkle",
    "petal",
    "pixel",
    "star",
    "bubble",
    "leaf",
    "music",
    "flame",
  ] as const
).map((value) => ({
  value,
  label: value,
  glyph: PARTICLE_GLYPHS[value][0],
}));
