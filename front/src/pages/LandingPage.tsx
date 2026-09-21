import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  CalendarHeart,
  Camera,
  Film,
  Gift,
  Heart,
  Images,
  Link2,
  Lock,
  MessageCircleHeart,
  Mic2,
  Music2,
  PartyPopper,
  Send,
  ShieldCheck,
  Sparkles,
  Star,
  Wand2,
  type LucideIcon,
} from "lucide-react";
import type { ReactNode } from "react";

import { designCoverUrl } from "../components/DesignCover";
import { DesignRatingStars } from "../components/DesignRatingStars";
import { PageTransition } from "../components/PageTransition";
import { api } from "../lib/api";
import { gradientCss, resolveTheme } from "../lib/theme";
import { useUiTheme } from "../hooks/useUiTheme";

type LandingTone = "hero" | "how" | "themes" | "features" | "cta";

function LandingBand({
  tone,
  id,
  className = "",
  innerClassName = "",
  children,
}: {
  tone: LandingTone;
  id?: string;
  className?: string;
  innerClassName?: string;
  children: ReactNode;
}) {
  return (
    <section
      id={id}
      className={`landing-band landing-band--${tone} ${className}`.trim()}
    >
      <div className={`landing-band__inner ${innerClassName}`.trim()}>
        {children}
      </div>
    </section>
  );
}

const ctaIcons: { Icon: LucideIcon; color: string }[] = [
  { Icon: Gift, color: "#e11d48" },
  { Icon: Heart, color: "#f43f5e" },
  { Icon: Camera, color: "#06b6d4" },
  { Icon: Sparkles, color: "#a855f7" },
  { Icon: Images, color: "#8b5cf6" },
  { Icon: Mic2, color: "#ec4899" },
  { Icon: Film, color: "#6366f1" },
  { Icon: CalendarHeart, color: "#f59e0b" },
  { Icon: PartyPopper, color: "#f97316" },
  { Icon: Music2, color: "#14b8a6" },
  { Icon: MessageCircleHeart, color: "#fb7185" },
  { Icon: Star, color: "#eab308" },
  { Icon: Lock, color: "#7c3aed" },
  { Icon: Link2, color: "#0ea5e9" },
  { Icon: Send, color: "#22d3ee" },
  { Icon: Wand2, color: "#d946ef" },
  { Icon: Gift, color: "#db2777" },
  { Icon: Heart, color: "#be185d" },
  { Icon: Camera, color: "#0891b2" },
  { Icon: Sparkles, color: "#c026d3" },
];

const workflowSteps = [
  {
    tone: "violet",
    title: "Создайте бокс",
    text: "Заполните основные поля: название, описание, получателя и тему оформления.",
    preview: "create",
  },
  {
    tone: "cyan",
    title: "Выберите дату и время",
    text: "Укажите момент открытия — до него бокс останется закрытым, без спойлеров.",
    preview: "timer",
  },
  {
    tone: "pink",
    title: "Наполните бокс",
    text: "Добавьте фото, видео, голосовые и текст — до 12 моментов в одном сюрпризе.",
    preview: "fill",
  },
  {
    tone: "amber",
    title: "Опубликуйте бокс",
    text: "Получите ссылку и пароль. Получателю уйдёт письмо на почту, вам — уведомление в Telegram.",
    preview: "publish",
  },
  {
    tone: "indigo",
    title: "Скачайте сертификат",
    text: "PDF с QR и паролем — можно распечатать и вложить в физический подарок.",
    preview: "certificate",
  },
  {
    tone: "emerald",
    title: "Откройте бокс",
    text: "В нужную секунду бокс оживёт у получателя, а вам придёт уведомление в Telegram.",
    preview: "open",
  },
] as const;

type WorkflowPreview = (typeof workflowSteps)[number]["preview"];

function WorkflowPreviewMock({ kind }: { kind: WorkflowPreview }) {
  if (kind === "create") {
    return (
      <div className="workflow-mock workflow-mock--form">
        <p className="workflow-mock__eyebrow">Новый бокс</p>
        <p className="workflow-mock__title">Основные поля</p>
        <div className="workflow-mock__field is-active">Получатель: Мария</div>
        <div className="workflow-mock__field">Название: День рождения</div>
        <div className="workflow-mock__field workflow-mock__field--muted">
          Описание сюрприза…
        </div>
        <div className="workflow-mock__btn">Далее</div>
      </div>
    );
  }
  if (kind === "timer") {
    return (
      <div className="workflow-mock workflow-mock--timer">
        <p className="workflow-mock__eyebrow">Дата и время</p>
        <div className="workflow-mock__digits">
          <span>
            <b>14</b>
            <small>мар</small>
          </span>
          <span>
            <b>19</b>
            <small>ч</small>
          </span>
          <span>
            <b>00</b>
            <small>м</small>
          </span>
        </div>
        <p className="workflow-mock__hint">Откроется ровно в эту секунду</p>
        <div className="workflow-mock__lock">
          <Lock className="size-3.5" />
          Без спойлеров до открытия
        </div>
      </div>
    );
  }
  if (kind === "fill") {
    return (
      <div className="workflow-mock workflow-mock--fill">
        <p className="workflow-mock__eyebrow">Содержимое</p>
        <p className="workflow-mock__title">Наполните бокс</p>
        <div className="workflow-mock__moments">
          <span>
            <Camera className="size-3" />
            Фото
          </span>
          <span>
            <Mic2 className="size-3" />
            Голос
          </span>
          <span>
            <Film className="size-3" />
            Видео
          </span>
          <span>
            <Heart className="size-3" />
            Текст
          </span>
        </div>
        <div className="workflow-mock__row">
          <span>Моментов</span>
          <strong>7 / 12</strong>
        </div>
        <div className="workflow-mock__btn">Добавить</div>
      </div>
    );
  }
  if (kind === "publish") {
    return (
      <div className="workflow-mock workflow-mock--publish">
        <p className="workflow-mock__eyebrow">Публикация</p>
        <p className="workflow-mock__title">Ссылка на бокс</p>
        <div className="workflow-mock__link">
          <Link2 className="size-3.5 shrink-0" />
          <span>pixelgift.app/b/maria</span>
        </div>
        <div className="workflow-mock__notify">
          <span>✉️ Почта получателю</span>
          <span>✈️ Telegram вам</span>
        </div>
        <div className="workflow-mock__btn">Опубликовать</div>
      </div>
    );
  }
  if (kind === "certificate") {
    return (
      <div className="workflow-mock workflow-mock--cert">
        <p className="workflow-mock__eyebrow">PDF · Pixelgift</p>
        <p className="workflow-mock__title">Сертификат подарка</p>
        <div className="workflow-mock__cert-card">
          <span className="workflow-mock__qr" aria-hidden />
          <div>
            <small>Для Марии</small>
            <strong>Открой бокс</strong>
          </div>
        </div>
        <div className="workflow-mock__btn">Скачать PDF</div>
      </div>
    );
  }
  return (
    <div className="workflow-mock workflow-mock--open">
      <div className="workflow-mock__gift">🎁</div>
      <p className="workflow-mock__title">Бокс открыт!</p>
      <div className="workflow-mock__moments">
        <span>
          <Camera className="size-3" />
          Фото
        </span>
        <span>
          <Mic2 className="size-3" />
          Голос
        </span>
        <span>
          <Heart className="size-3" />
          Письмо
        </span>
      </div>
      <div className="workflow-mock__btn is-soft">Смотреть моменты</div>
    </div>
  );
}

function WorkflowCard({
  step,
  index,
}: {
  step: (typeof workflowSteps)[number];
  index: number;
}) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ delay: index * 0.06, duration: 0.45 }}
      className={`workflow-card workflow-card--${step.tone}`}
    >
      <div className="workflow-card__preview">
        <WorkflowPreviewMock kind={step.preview} />
      </div>
      <div className="workflow-card__body">
        <span className="workflow-card__num">{index + 1}</span>
        <h3>{step.title}</h3>
        <p>{step.text}</p>
      </div>
    </motion.article>
  );
}

const features = [
  {
    icon: Lock,
    title: "Ничего не спойлерится",
    text: "До активации по ссылке видно только превью и обратный отсчёт.",
  },
  {
    icon: Sparkles,
    title: "Живое оформление",
    text: "Каждая тема со своими градиентами, частицами и анимацией открытия.",
  },
  {
    icon: Link2,
    title: "Вход за один тап",
    text: "Авторизация через Telegram-бота — без паролей и почты.",
  },
];

export function LandingPage() {
  const { theme: uiTheme } = useUiTheme();
  const { data: designs = [] } = useQuery({
    queryKey: ["designs"],
    queryFn: api.designs,
  });

  return (
    <PageTransition>
      <LandingBand
        tone="hero"
        className="landing-hero"
        innerClassName="relative grid min-h-[calc(100dvh-4rem)] items-center gap-8 py-12 lg:grid-cols-[0.9fr_1.1fr] lg:gap-4 lg:py-20"
      >
        <div className="relative z-10 text-center lg:text-left">
          <motion.span
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="chip"
          >
            <Sparkles className="size-3.5 text-glow-gold" />
            Подарок, который умеет ждать
          </motion.span>

          <motion.h1
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 }}
            className="font-display mt-6 text-4xl leading-[1.08] tracking-tight sm:text-6xl lg:text-[3.6rem]"
          >
            Соберите эмоции. <span className="text-gradient">Подарите момент.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.16 }}
            className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-slate-400 sm:text-lg lg:mx-0"
          >
            Фото, видео и голосовые оживут внутри волшебного бокса — ровно в ту
            секунду, которую выберете вы.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.24 }}
            className="mt-9 flex flex-wrap items-center justify-center gap-3 lg:justify-start"
          >
            <Link to="/login" className="btn-primary px-7 py-3.5 text-base">
              <Gift className="size-5" />
              Создать подарок
            </Link>
            <a href="#how" className="btn-ghost px-7 py-3.5 text-base">
              Посмотреть как
            </a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.36 }}
            className="mt-7 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-xs text-slate-500 lg:justify-start"
          >
            <span className="inline-flex items-center gap-1.5">
              <ShieldCheck className="size-4 text-emerald-400" />
              Без спойлеров
            </span>
            <span>Без паролей</span>
            <span>Первый бокс — бесплатно</span>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.92, x: 30 }}
          animate={{ opacity: 1, scale: 1, x: 0 }}
          transition={{ delay: 0.12, duration: 0.65, ease: "easeOut" }}
          className="hero-visual relative mx-auto w-full max-w-[720px]"
        >
          <div className="hero-visual__halo" />
          <img
            src="/pixelgift-hero.jpg"
            alt="Цифровой подарочный бокс с фотографиями, голосовым сообщением и сияющими сердцами"
            className="hero-visual__image relative z-10 w-full"
          />
          <motion.div
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="hero-float-card hero-float-card--media"
          >
            <span className="grid size-9 place-items-center rounded-xl bg-pink-400/15 text-pink-300">
              <Heart className="size-4 fill-current" />
            </span>
            <span>
              <b>12 моментов</b>
              <small>бережно внутри</small>
            </span>
          </motion.div>
          <motion.div
            animate={{ y: [0, 7, 0] }}
            transition={{ duration: 4.6, repeat: Infinity, ease: "easeInOut" }}
            className="hero-float-card hero-float-card--timer"
          >
            <Mic2 className="size-4 text-glow-cyan" />
            <span className="font-mono text-sm text-slate-100">00:18</span>
            <span className="flex items-end gap-0.5">
              {[8, 14, 10, 18, 12].map((height, index) => (
                <i
                  key={index}
                  className="w-0.5 rounded-full bg-glow-cyan"
                  style={{ height }}
                />
              ))}
            </span>
          </motion.div>
        </motion.div>
      </LandingBand>

      <LandingBand tone="how" id="how" className="scroll-mt-24" innerClassName="py-16 sm:py-20">
        <div className="mx-auto max-w-2xl text-center">
          <div className="section-kicker">Как это работает</div>
          <h2 className="font-display text-3xl tracking-tight sm:text-4xl">
            От идеи до открытия —{" "}
            <span className="text-gradient">шесть понятных шагов</span>
          </h2>
          <p className="mt-4 text-sm leading-relaxed text-slate-400 sm:text-base">
            Создайте бокс, задайте время, наполните и опубликуйте. Получатель
            узнает о подарке по почте, а вам придёт уведомление в Telegram —
            когда бокс опубликован и когда его откроют.
          </p>
        </div>

        <div className="workflow-grid mt-10">
          {workflowSteps.map((step, index) => (
            <WorkflowCard key={step.title} step={step} index={index} />
          ))}
        </div>

        <div className="mt-10 flex justify-center">
          <Link to="/login" className="btn-primary px-8 py-3.5 text-base">
            <Gift className="size-5" />
            Создать подарок
          </Link>
        </div>
      </LandingBand>

      {designs.length > 0 && (
        <LandingBand tone="themes" innerClassName="py-16">
          <div className="section-kicker">Каждому моменту — своё настроение</div>
          <h2 className="font-display text-center text-3xl tracking-tight sm:text-4xl">
            Темы оформления
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-sm text-slate-400">
            Оформление меняет фон, частицы и анимацию открытия — бокс выглядит как
            отдельный маленький сайт.
          </p>
          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {designs.map((design, index) => {
              const theme = resolveTheme(design);

              return (
                <motion.article
                  key={design.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-60px" }}
                  transition={{ delay: index * 0.05 }}
                  className="design-banner"
                  style={{ background: gradientCss(theme.gradient) }}
                >
                  <img
                    src={designCoverUrl(design, uiTheme)}
                    alt=""
                    loading="lazy"
                    className="design-banner__image"
                    onError={(event) => {
                      event.currentTarget.style.display = "none";
                    }}
                  />
                  <div className="design-banner__blur" aria-hidden>
                    <img
                      src={designCoverUrl(design, uiTheme)}
                      alt=""
                      loading="lazy"
                      className="design-banner__blur-image"
                      onError={(event) => {
                        event.currentTarget.style.display = "none";
                      }}
                    />
                  </div>
                  <div className="design-banner__scrim" />

                  <div className="design-banner__content">
                    <h3 className="design-banner__title">{design.name}</h3>
                    {design.description && (
                      <p className="design-banner__pill">{design.description}</p>
                    )}
                    <DesignRatingStars
                      average={design.rating_avg ?? 0}
                      count={design.rating_count ?? 0}
                      myRating={design.my_rating ?? null}
                      className="mt-2"
                    />
                    <Link to="/login" className="design-banner__cta">
                      Собрать в этой теме
                    </Link>
                  </div>
                </motion.article>
              );
            })}
          </div>
        </LandingBand>
      )}

      <LandingBand tone="features" innerClassName="py-16">
        <div className="section-kicker">Магия с продуманными деталями</div>
        <div className="grid gap-4 sm:grid-cols-3">
          {features.map((feature) => (
            <div key={feature.title} className="glass-soft p-6">
              <feature.icon className="size-5 text-glow-cyan" />
              <h3 className="mt-4 text-base font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">
                {feature.text}
              </p>
            </div>
          ))}
        </div>
      </LandingBand>

      <LandingBand tone="cta" className="landing-cta relative overflow-hidden">
        <div className="landing-cta__inner relative z-[1] grid items-center lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
          <div className="landing-cta__copy px-6 py-7 text-left sm:px-10 sm:py-8 lg:px-12 lg:py-9">
            <h2 className="font-display text-2xl tracking-tight text-white sm:text-3xl">
              Подарите не файл, а момент
            </h2>
            <p className="mt-2.5 max-w-md text-sm leading-relaxed text-white/80">
              Вход через Telegram занимает пару секунд. Первый бокс можно собрать за
              пять минут.
            </p>
            <Link
              to="/login"
              className="landing-cta__btn mt-5 inline-flex px-6 py-3 text-sm sm:text-base"
            >
              Начать бесплатно
            </Link>
          </div>

          <div className="landing-cta__visual" aria-hidden>
            <div className="landing-cta__mosaic">
              {ctaIcons.map(({ Icon, color }, index) => (
                <div key={`${color}-${index}`} className="landing-cta__tile">
                  <Icon style={{ color }} strokeWidth={2.1} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </LandingBand>
    </PageTransition>
  );
}
