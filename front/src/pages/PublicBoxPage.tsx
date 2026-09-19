import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, Gift, Heart, KeyRound, Lock, Sparkles } from "lucide-react";

import { ConfettiBurst } from "../components/ConfettiBurst";
import { CountdownTimer } from "../components/CountdownTimer";
import { GiftBox3D, resolveGiftBoxPalette } from "../components/GiftBox3D";
import { MediaPreview } from "../components/MediaPreview";
import { Particles } from "../components/Particles";
import { ScratchReveal } from "../components/ScratchReveal";
import { Spinner } from "../components/Spinner";
import { ApiError, api, publicMediaUrl } from "../lib/api";
import { formatDateTime } from "../lib/format";
import { getMediaKindOption } from "../lib/mediaKinds";
import { isSecretPhotoItem } from "../lib/secret";
import { radialGlowCss, resolveTheme, themeBackgroundLayers } from "../lib/theme";
import type { BoxItem, PublicBox } from "../lib/types";
import { geopointFromMetadata } from "../lib/geopoint";
import { toyCodeFromMetadata, toyImageUrl } from "../lib/toys";

function unlockStorageKey(slug: string) {
  return `pixelgift-unlock:${slug}`;
}

function readUnlockToken(slug: string): string | null {
  try {
    return sessionStorage.getItem(unlockStorageKey(slug));
  } catch {
    return null;
  }
}

function writeUnlockToken(slug: string, token: string | null) {
  try {
    if (token) sessionStorage.setItem(unlockStorageKey(slug), token);
    else sessionStorage.removeItem(unlockStorageKey(slug));
  } catch {
    /* ignore */
  }
}

type RevealStep =
  | { kind: "intro" }
  | { kind: "letter" }
  | { kind: "item"; item: BoxItem; index: number; total: number }
  | { kind: "finale" };

function buildSteps(box: PublicBox): RevealStep[] {
  const steps: RevealStep[] = [{ kind: "intro" }];
  if (box.message || box.title) {
    steps.push({ kind: "letter" });
  }
  box.items.forEach((item, index) => {
    steps.push({ kind: "item", item, index, total: box.items.length });
  });
  steps.push({ kind: "finale" });
  return steps;
}

const slideVariants = {
  enter: (direction: number) => ({
    opacity: 0,
    x: direction > 0 ? 56 : -56,
    scale: 0.94,
    filter: "blur(8px)",
  }),
  center: {
    opacity: 1,
    x: 0,
    scale: 1,
    filter: "blur(0px)",
  },
  exit: (direction: number) => ({
    opacity: 0,
    x: direction > 0 ? -48 : 48,
    scale: 1.04,
    filter: "blur(6px)",
  }),
};

export function PublicBoxPage() {
  const { slug = "" } = useParams<{ slug: string }>();
  const queryClient = useQueryClient();
  const [stepIndex, setStepIndex] = useState(0);
  const [direction, setDirection] = useState(1);
  const [confetti, setConfetti] = useState(false);
  const [secretRevealed, setSecretRevealed] = useState(true);
  const [unlockToken, setUnlockToken] = useState<string | null>(() =>
    slug ? readUnlockToken(slug) : null,
  );
  const [passwordInput, setPasswordInput] = useState("");
  const [passwordError, setPasswordError] = useState<string | null>(null);

  useEffect(() => {
    setUnlockToken(slug ? readUnlockToken(slug) : null);
    setPasswordInput("");
    setPasswordError(null);
    setStepIndex(0);
  }, [slug]);

  const boxQuery = useQuery({
    queryKey: ["public-box", slug, unlockToken],
    queryFn: () => api.publicBox(slug, unlockToken),
    enabled: Boolean(slug),
  });

  const unlockMutation = useMutation({
    mutationFn: (password: string) => api.unlockPublicBox(slug, password),
    onSuccess: (result) => {
      if (result.unlock_token) {
        writeUnlockToken(slug, result.unlock_token);
        setUnlockToken(result.unlock_token);
      }
      queryClient.setQueryData(["public-box", slug, result.unlock_token], result.box);
      setPasswordError(null);
      setPasswordInput("");
    },
    onError: (error) => {
      const message =
        error instanceof ApiError && error.status === 403
          ? "Неверный пароль"
          : "Не удалось открыть бокс";
      setPasswordError(message);
    },
  });

  const box = boxQuery.data;
  const theme = resolveTheme(box?.theme_config ?? null);
  const giftPalette = useMemo(
    () => resolveGiftBoxPalette(theme.gift_box, theme.gradient, theme.accent),
    [theme.gift_box, theme.gradient, theme.accent],
  );

  const steps = useMemo(() => (box ? buildSteps(box) : []), [box]);
  const step = steps[stepIndex] ?? null;
  const isLast = stepIndex >= steps.length - 1;
  const needsSecretScratch =
    step?.kind === "item" && isSecretPhotoItem(step.item);
  const canGoNext = !needsSecretScratch || secretRevealed;

  useEffect(() => {
    setSecretRevealed(!(step?.kind === "item" && isSecretPhotoItem(step.item)));
  }, [step]);

  const refetchOnUnlock = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ["public-box", slug] });
  }, [queryClient, slug]);

  const goNext = useCallback(() => {
    if (!steps.length || isLast) return;
    setDirection(1);
    setStepIndex((current) => Math.min(current + 1, steps.length - 1));
  }, [isLast, steps.length]);

  useEffect(() => {
    if (!step) return;
    if (step.kind === "intro" || step.kind === "finale" || step.kind === "letter") {
      setConfetti(true);
      const timer = window.setTimeout(() => setConfetti(false), 2200);
      return () => window.clearTimeout(timer);
    }
  }, [step]);

  if (boxQuery.isPending) {
    return (
      <div className="theme-canvas grid min-h-dvh place-items-center">
        <Spinner label="Открываем бокс…" />
      </div>
    );
  }

  if (boxQuery.isError || !box) {
    return (
      <div className="theme-canvas grid min-h-dvh place-items-center px-6 text-center">
        <div className="glass max-w-md p-10">
          <span className="text-4xl">🕳️</span>
          <h1 className="font-display mt-5 text-2xl">Подарок не найден</h1>
          <p className="mt-3 text-sm text-slate-400">
            Ссылка неверна, бокс ещё не опубликован или его убрали в архив.
          </p>
          <Link to="/" className="btn-ghost mt-7">
            На главную
          </Link>
        </div>
      </div>
    );
  }

  const locked = !box.content_unlocked;
  const waitingForTimer = locked && new Date(box.activates_at).getTime() > Date.now();
  const needsPassword =
    locked && !waitingForTimer && box.password_required;
  const progress = steps.length > 1 ? stepIndex / (steps.length - 1) : 0;
  const bgLayers = themeBackgroundLayers(theme);

  return (
    <div
      className="public-box-page relative min-h-dvh overflow-hidden px-4 py-10 sm:px-6 sm:py-14"
      style={{ ...bgLayers, color: theme.text }}
    >
      {theme.background_image_url ? (
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{ background: "linear-gradient(165deg, rgb(0 0 0 / 0.55), rgb(0 0 0 / 0.35))" }}
        />
      ) : null}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{ background: radialGlowCss(theme.accent) }}
      />
      <Particles particle={theme.particle} accent={theme.accent} />
      {confetti && (
        <ConfettiBurst colors={[theme.accent, "#ffffff", ...theme.gradient]} />
      )}

      <div className="relative mx-auto flex min-h-[calc(100dvh-5rem)] max-w-3xl flex-col">
        {waitingForTimer && (
          <motion.section
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass my-auto w-full min-w-0 overflow-hidden px-6 py-14 text-center sm:px-12"
          >
            <span className="chip mx-auto" style={{ borderColor: `${theme.accent}55` }}>
              <Lock className="size-3.5" />
              Пока закрыто
            </span>

            <div className="mt-8 flex justify-center">
              <GiftBox3D
                palette={giftPalette}
                size="lg"
              />
            </div>

            <h1 className="font-display mt-6 max-w-full break-words text-3xl leading-tight [overflow-wrap:anywhere] sm:text-4xl">
              {box.preview_title ?? `${box.recipient_name}, для тебя есть подарок`}
            </h1>

            <p className="mt-4 text-sm opacity-75">
              Откроется {formatDateTime(box.activates_at)}
            </p>

            <div className="mt-10">
              <CountdownTimer
                activatesAt={box.activates_at}
                accent={theme.accent}
                onFinish={refetchOnUnlock}
              />
            </div>

            <p className="mx-auto mt-10 max-w-sm text-xs opacity-60">
              {box.password_required
                ? "После таймера понадобится пароль из письма."
                : "Возвращайтесь в назначенный момент — содержимое появится автоматически."}
            </p>
          </motion.section>
        )}

        {needsPassword && (
          <motion.section
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass my-auto w-full min-w-0 overflow-hidden px-6 py-14 text-center sm:px-12"
          >
            <span className="chip mx-auto" style={{ borderColor: `${theme.accent}55` }}>
              <KeyRound className="size-3.5" />
              Нужен пароль
            </span>

            <div className="mt-8 flex justify-center">
              <GiftBox3D palette={giftPalette} size="lg" />
            </div>

            <h1 className="font-display mt-6 max-w-full break-words text-3xl leading-tight [overflow-wrap:anywhere] sm:text-4xl">
              {box.preview_title ?? `${box.recipient_name}, для тебя есть подарок`}
            </h1>

            <p className="mx-auto mt-4 max-w-sm text-sm opacity-75">
              Введите пароль из письма, чтобы открыть бокс
            </p>

            <form
              className="mx-auto mt-8 flex w-full max-w-xs flex-col gap-3"
              onSubmit={(event) => {
                event.preventDefault();
                const value = passwordInput.trim();
                if (!value) {
                  setPasswordError("Введите пароль");
                  return;
                }
                unlockMutation.mutate(value);
              }}
            >
              <input
                className="field text-center font-mono tracking-[0.18em]"
                value={passwordInput}
                maxLength={12}
                autoComplete="off"
                spellCheck={false}
                placeholder="Пароль"
                onChange={(event) => {
                  setPasswordInput(event.target.value.replace(/[^A-Za-z0-9]/g, ""));
                  setPasswordError(null);
                }}
              />
              {passwordError ? (
                <p className="text-xs text-rose-300">{passwordError}</p>
              ) : null}
              <button
                type="submit"
                className="btn-primary justify-center"
                disabled={unlockMutation.isPending || passwordInput.trim().length < 4}
              >
                {unlockMutation.isPending ? "Проверяем…" : "Открыть"}
              </button>
            </form>
          </motion.section>
        )}

        {!locked && step && (
          <>
            {step.kind !== "intro" && (
              <div className="mb-6">
                <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ background: theme.accent }}
                    initial={false}
                    animate={{ width: `${Math.max(progress, 0.04) * 100}%` }}
                    transition={{ type: "spring", stiffness: 120, damping: 20 }}
                  />
                </div>
                <p className="mt-2 text-center text-[0.7rem] tracking-wide opacity-55 uppercase">
                  Шаг {stepIndex + 1} из {steps.length}
                </p>
              </div>
            )}

            <div className="relative flex flex-1 flex-col justify-center">
              <AnimatePresence mode="wait" custom={direction}>
                <motion.div
                  key={`${step.kind}-${"item" in step ? step.item.id : step.kind}`}
                  custom={direction}
                  variants={slideVariants}
                  initial="enter"
                  animate="center"
                  exit="exit"
                  transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                  className="w-full"
                >
                  {step.kind === "intro" && (
                    <IntroStep
                      box={box}
                      accent={theme.accent}
                      palette={giftPalette}
                      onOpen={goNext}
                    />
                  )}

                  {step.kind === "letter" && (
                    <LetterStep box={box} accent={theme.accent} />
                  )}

                  {step.kind === "item" && (
                    <ItemStep
                      box={box}
                      item={step.item}
                      index={step.index}
                      total={step.total}
                      accent={theme.accent}
                      unlockToken={unlockToken}
                      onSecretRevealed={() => setSecretRevealed(true)}
                    />
                  )}

                  {step.kind === "finale" && (
                    <FinaleStep box={box} accent={theme.accent} />
                  )}
                </motion.div>
              </AnimatePresence>
            </div>

            {step.kind !== "intro" && (
              <div className="mt-8 flex flex-col items-center gap-2 pb-2">
                {!isLast ? (
                  <>
                    <motion.button
                      type="button"
                      disabled={!canGoNext}
                      whileHover={canGoNext ? { scale: 1.04 } : undefined}
                      whileTap={canGoNext ? { scale: 0.97 } : undefined}
                      onClick={goNext}
                      className="btn px-8 py-3.5 text-base font-bold disabled:cursor-not-allowed disabled:opacity-45"
                      style={{
                        background: theme.accent,
                        color: "#0b0718",
                        boxShadow: canGoNext
                          ? `0 20px 50px -20px ${theme.accent}`
                          : undefined,
                      }}
                    >
                      Далее
                      <ArrowRight className="size-5" />
                    </motion.button>
                    {needsSecretScratch && !secretRevealed ? (
                      <p className="text-center text-xs opacity-60">
                        Сначала сотри слой, чтобы увидеть фото
                      </p>
                    ) : null}
                  </>
                ) : (
                  <Link
                    to="/"
                    className="btn-ghost px-6 py-3 text-sm"
                    style={{ borderColor: `${theme.accent}44` }}
                  >
                    Собрано в Pixelgift
                  </Link>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function IntroStep({
  box,
  accent,
  palette,
  onOpen,
}: {
  box: PublicBox;
  accent: string;
  palette: ReturnType<typeof resolveGiftBoxPalette>;
  onOpen: () => void;
}) {
  const [opening, setOpening] = useState(false);

  const handleOpen = () => {
    if (opening) return;
    setOpening(true);
    window.setTimeout(() => onOpen(), 1000);
  };

  return (
    <section className="glass px-6 py-16 text-center sm:px-12">
      <GiftBox3D
        palette={palette}
        opening={opening}
        size="lg"
        className="mx-auto"
      />

      <h1 className="font-display mt-8 text-3xl leading-tight sm:text-4xl">
        {box.recipient_name}, время открывать!
      </h1>
      <p className="mt-4 text-sm opacity-75">Бокс уже разблокирован</p>

      <motion.button
        type="button"
        disabled={opening}
        whileHover={opening ? undefined : { scale: 1.04 }}
        whileTap={opening ? undefined : { scale: 0.97 }}
        onClick={handleOpen}
        className="btn mt-10 px-8 py-4 text-base font-bold disabled:opacity-70"
        style={{
          background: accent,
          color: "#0b0718",
          boxShadow: `0 20px 50px -20px ${accent}`,
        }}
      >
        <Gift className="size-5" />
        {opening ? "Открываем…" : "Открыть подарок"}
      </motion.button>
    </section>
  );
}

function LetterStep({
  box,
  accent,
}: {
  box: PublicBox;
  accent: string;
}) {
  return (
    <section className="glass w-full min-w-0 overflow-hidden px-6 py-12 text-center sm:px-12">
      <motion.div
        initial={{ scale: 0.6, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 180, damping: 14 }}
        className="mx-auto grid size-14 place-items-center rounded-full"
        style={{ background: `${accent}22`, color: accent }}
      >
        <Heart className="size-7" fill="currentColor" />
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="font-display mt-6 max-w-full break-words text-3xl leading-tight [overflow-wrap:anywhere] sm:text-4xl"
      >
        {box.title}
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.7 }}
        transition={{ delay: 0.25 }}
        className="mt-3 text-sm"
      >
        Для {box.recipient_name}
      </motion.p>

      {box.message && (
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 0.95, y: 0 }}
          transition={{ delay: 0.35 }}
          className="mx-auto mt-8 max-w-xl break-words text-base leading-relaxed whitespace-pre-line [overflow-wrap:anywhere] sm:text-lg"
          style={{ borderColor: `${accent}33` }}
        >
          {box.message}
        </motion.p>
      )}
    </section>
  );
}

function ItemStep({
  box,
  item,
  index,
  total,
  accent,
  unlockToken,
  onSecretRevealed,
}: {
  box: PublicBox;
  item: BoxItem;
  index: number;
  total: number;
  accent: string;
  unlockToken?: string | null;
  onSecretRevealed?: () => void;
}) {
  const secret = isSecretPhotoItem(item);
  const previewClassName =
    item.item_type === "circle"
      ? "size-[min(70vw,20rem)] sm:size-[min(58dvh,22rem)]"
      : item.item_type === "voice" ||
          item.item_type === "text" ||
          item.item_type === "geopoint"
        ? "w-full rounded-2xl"
        : secret
          ? "!h-auto !w-auto max-h-[min(58dvh,32rem)] max-w-full"
          : "max-h-[min(58dvh,32rem)] rounded-2xl";

  const preview = (
    <MediaPreview
      src={
        item.item_type === "toy"
          ? toyImageUrl(toyCodeFromMetadata(item.metadata) ?? "bear")
          : item.media_file_id
            ? publicMediaUrl(box.public_slug, item.id, unlockToken)
            : ""
      }
      type={item.item_type}
      fit="contain"
      caption={item.caption}
      toyCode={toyCodeFromMetadata(item.metadata)}
      geopoint={geopointFromMetadata(item.metadata)}
      metadata={item.metadata}
      className={previewClassName}
    />
  );

  return (
    <section className="glass overflow-hidden">
      <div className="flex items-center justify-between gap-4 px-6 py-4 text-xs opacity-70 sm:px-8 sm:py-5">
        <span className="inline-flex items-center gap-1.5">
          <Sparkles className="size-3.5" style={{ color: accent }} />
          Воспоминание {index + 1} из {total}
        </span>
        <span>{getMediaKindOption(item.item_type).label}</span>
      </div>

      <div className="relative mx-auto flex min-h-[18rem] max-h-[min(62dvh,34rem)] w-full items-center justify-center bg-black/25 px-3 py-4 sm:min-h-[22rem] sm:px-5">
        {secret ? (
          <ScratchReveal
            className="max-h-[min(58dvh,32rem)] w-full max-w-full rounded-2xl"
            accent={accent}
            onRevealed={onSecretRevealed}
          >
            {preview}
          </ScratchReveal>
        ) : (
          preview
        )}
      </div>

      {item.item_type !== "voice" &&
      item.item_type !== "text" &&
      item.caption ? (
        <motion.p
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="px-6 py-5 text-center text-base leading-relaxed opacity-90 sm:px-10 sm:text-lg"
        >
          {item.caption}
        </motion.p>
      ) : (
        <div className={item.item_type === "text" ? "h-6 sm:h-8" : "h-4"} />
      )}
    </section>
  );
}

function FinaleStep({
  box,
  accent,
}: {
  box: PublicBox;
  accent: string;
}) {
  return (
    <section className="glass px-6 py-16 text-center sm:px-12">
      <motion.div
        initial={{ scale: 0.5, rotate: -20 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 160, damping: 12 }}
        className="mx-auto grid size-16 place-items-center rounded-full"
        style={{ background: `${accent}22`, color: accent }}
      >
        <Sparkles className="size-8" />
      </motion.div>

      <h1 className="font-display mt-7 text-3xl leading-tight sm:text-4xl">
        Вот и всё, {box.recipient_name}
      </h1>
      <p className="mx-auto mt-4 max-w-md text-sm leading-relaxed opacity-75">
        Подарок открыт. Можешь вернуться к любимым моментам — они уже с тобой.
      </p>

      <motion.div
        animate={{ scale: [1, 1.15, 1] }}
        transition={{ duration: 1.6, repeat: Infinity }}
        className="mt-8 inline-flex"
        style={{ color: accent }}
      >
        <Heart className="size-8 fill-current" />
      </motion.div>
    </section>
  );
}
