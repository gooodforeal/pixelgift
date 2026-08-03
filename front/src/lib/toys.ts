/** Catalog of preset plush toys for box items of type `toy`. */

export interface ToyOption {
  code: string;
  name: string;
  description: string;
}

export const TOY_OPTIONS: ToyOption[] = [
  {
    code: "bear",
    name: "Мишка",
    description: "Обнимет крепче всех и будет ждать тебя до самой встречи",
  },
  {
    code: "bunny",
    name: "Зайчик",
    description: "Мягкие ушки и розовый бантик — для самого нежного «люблю»",
  },
  {
    code: "fox",
    name: "Лисичка",
    description: "Хитрая, но добрая — спрячет тепло твоих слов в пушистом хвосте",
  },
  {
    code: "kitty",
    name: "Котик",
    description: "Мурлычет от счастья и дарит уют в любой день",
  },
  {
    code: "penguin",
    name: "Пингвинчик",
    description: "Пришёл из холодных краёв, чтобы согреть твоё сердце",
  },
  {
    code: "dino",
    name: "Динозаврик",
    description: "Маленький, но храбрый страж твоих самых тёплых моментов",
  },
];

export const TOY_CODES = new Set(TOY_OPTIONS.map((toy) => toy.code));

export function getToyOption(code: string | null | undefined): ToyOption | null {
  if (!code) return null;
  return TOY_OPTIONS.find((toy) => toy.code === code) ?? null;
}

export function toyImageUrl(code: string): string {
  return `/toys/${code}.png`;
}

export function toyCodeFromMetadata(
  metadata: Record<string, unknown> | null | undefined,
): string | null {
  const value = metadata?.toy_code;
  return typeof value === "string" && TOY_CODES.has(value) ? value : null;
}
