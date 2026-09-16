import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  CalendarClock,
  Gift,
  Heart,
  Images,
  Link2,
  Lock,
  Mic2,
  Send,
  ShieldCheck,
  Sparkles,
  Wand2,
} from "lucide-react";

import { designCoverUrl } from "../components/DesignCover";
import { DesignRatingStars } from "../components/DesignRatingStars";
import { PageTransition } from "../components/PageTransition";
import { api } from "../lib/api";
import { gradientCss, resolveTheme } from "../lib/theme";
import { useUiTheme } from "../hooks/useUiTheme";

const steps = [
  {
    icon: Wand2,
    title: "Выберите оформление",
    text: "Шесть тем — от романтичной ночи до пиксельного ретро.",
  },
  {
    icon: Images,
    title: "Наполните бокс",
    text: "Фото, гифки, видео и голосовые с подписями в нужном порядке.",
  },
  {
    icon: CalendarClock,
    title: "Задайте дату",
    text: "Бокс откроется секунда в секунду в выбранный момент.",
  },
  {
    icon: Send,
    title: "Отправьте ссылку",
    text: "Получателю не нужен аккаунт — только одна ссылка.",
  },
];

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
      <section className="landing-hero relative grid min-h-[calc(100dvh-4rem)] items-center gap-8 py-12 lg:grid-cols-[0.9fr_1.1fr] lg:gap-4 lg:py-20">
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
      </section>

      <section id="how" className="scroll-mt-24 py-16">
        <div className="section-kicker">Просто и по-настоящему лично</div>
        <h2 className="font-display text-center text-3xl tracking-tight sm:text-4xl">
          Четыре шага до сюрприза
        </h2>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ delay: index * 0.07 }}
              className="landing-step glass-soft relative overflow-hidden p-6"
            >
              <span className="landing-step__glow" />
              <div className="flex items-center justify-between">
                <span className="grid size-11 place-items-center rounded-2xl bg-glow-violet/15 text-glow-violet">
                  <step.icon className="size-5" />
                </span>
                <span className="font-display text-2xl text-white/10">
                  0{index + 1}
                </span>
              </div>
              <h3 className="mt-4 text-base font-semibold">{step.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">{step.text}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {designs.length > 0 && (
        <section className="py-16">
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
                    <Link
                      to="/login"
                      className="design-banner__cta"
                      style={{ backgroundColor: theme.accent }}
                    >
                      Собрать в этой теме
                    </Link>
                  </div>
                </motion.article>
              );
            })}
          </div>
        </section>
      )}

      <section className="py-16">
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
      </section>

      <section className="landing-cta glass relative overflow-hidden px-6 py-14 text-center sm:px-12">
        <div
          className="pointer-events-none absolute inset-x-0 -top-32 h-64 opacity-40 blur-3xl"
          style={{ background: gradientCss(["#f472b6", "#a855f7", "#22d3ee"], 90) }}
        />
        <Gift className="relative mx-auto mb-5 size-9 text-glow-gold" />
        <h2 className="font-display relative text-3xl tracking-tight sm:text-4xl">
          Подарите не файл, а момент
        </h2>
        <p className="relative mx-auto mt-4 max-w-lg text-sm text-slate-600">
          Вход через Telegram занимает пару секунд. Первый бокс можно собрать за пять
          минут.
        </p>
        <Link to="/login" className="btn-primary relative mt-8 px-7 py-3.5 text-base">
          Начать бесплатно
        </Link>
      </section>
    </PageTransition>
  );
}
