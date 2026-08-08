import type { BoxItemType } from "./types";

export interface MediaKindOption {
  kind: BoxItemType;
  label: string;
  /** Full formats — shown in the dropzone. */
  hint: string;
  /** Compact formats for the type picker chips. */
  shortHint: string;
  accept: string;
  extensions: string[];
  mimeTypes: string[];
  /** Text cards do not upload files. */
  isText?: boolean;
  /** Toy cards pick a preset plush from the catalog. */
  isToy?: boolean;
  /** Geopoint cards pick a location on the map. */
  isGeopoint?: boolean;
}

export const MEDIA_KIND_OPTIONS: MediaKindOption[] = [
  {
    kind: "image",
    label: "Фото",
    hint: "JPEG, PNG, WebP",
    shortHint: "JPEG · PNG · WebP",
    accept: "image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp",
    extensions: [".jpg", ".jpeg", ".png", ".webp"],
    mimeTypes: ["image/jpeg", "image/png", "image/webp"],
  },
  {
    kind: "gif",
    label: "GIF",
    hint: "Анимированные GIF",
    shortHint: "Анимация",
    accept: "image/gif,.gif",
    extensions: [".gif"],
    mimeTypes: ["image/gif"],
  },
  {
    kind: "video",
    label: "Видео",
    hint: "MP4, WebM, MOV",
    shortHint: "MP4 · WebM · MOV",
    accept: "video/mp4,video/webm,video/quicktime,video/x-mov,.mp4,.webm,.mov",
    extensions: [".mp4", ".webm", ".mov"],
    mimeTypes: ["video/mp4", "video/webm", "video/quicktime", "video/x-mov"],
  },
  {
    kind: "voice",
    label: "Аудио",
    hint: "MP3, OGG, M4A, WAV, WebM",
    shortHint: "MP3 · OGG · WAV",
    accept:
      "audio/mpeg,audio/ogg,audio/webm,audio/mp4,audio/wav,audio/x-wav,audio/x-m4a,.mp3,.ogg,.m4a,.wav,.webm",
    extensions: [".mp3", ".ogg", ".oga", ".opus", ".m4a", ".wav", ".webm"],
    mimeTypes: [
      "audio/mpeg",
      "audio/mp3",
      "audio/ogg",
      "audio/webm",
      "audio/mp4",
      "audio/x-m4a",
      "audio/wav",
      "audio/x-wav",
    ],
  },
  {
    kind: "text",
    label: "Текст",
    hint: "Сообщение без файла",
    shortHint: "Без файла",
    accept: "",
    extensions: [],
    mimeTypes: [],
    isText: true,
  },
  {
    kind: "toy",
    label: "Игрушка",
    hint: "Плюшевый подарок из каталога",
    shortHint: "Каталог",
    accept: "",
    extensions: [],
    mimeTypes: [],
    isToy: true,
  },
  {
    kind: "geopoint",
    label: "Геоточка",
    hint: "Точка на карте",
    shortHint: "Карта",
    accept: "",
    extensions: [],
    mimeTypes: [],
    isGeopoint: true,
  },
];

export function getMediaKindOption(kind: BoxItemType): MediaKindOption {
  return MEDIA_KIND_OPTIONS.find((option) => option.kind === kind) ?? MEDIA_KIND_OPTIONS[0];
}

export function fileMatchesMediaKind(file: File, kind: BoxItemType): boolean {
  const option = getMediaKindOption(kind);
  if (option.isText || option.isToy || option.isGeopoint) return false;
  const mime = file.type.toLowerCase();
  if (mime && option.mimeTypes.includes(mime)) return true;

  const name = file.name.toLowerCase();
  return option.extensions.some((ext) => name.endsWith(ext));
}

export function filterFilesByMediaKind(
  files: File[],
  kind: BoxItemType,
): { accepted: File[]; rejected: File[] } {
  const accepted: File[] = [];
  const rejected: File[] = [];
  for (const file of files) {
    if (fileMatchesMediaKind(file, kind)) accepted.push(file);
    else rejected.push(file);
  }
  return { accepted, rejected };
}
