import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { RefreshCw, ShieldCheck } from "lucide-react";
import QRCode from "qrcode";

import { PageTransition } from "../components/PageTransition";
import { Spinner } from "../components/Spinner";
import { TelegramIcon } from "../components/TelegramIcon";
import { useToast } from "../components/Toast";
import { useAuth } from "../hooks/useAuth";
import { api } from "../lib/api";
import type { TelegramLoginStart } from "../lib/types";

function isChallengeTimedOut(challenge: TelegramLoginStart | null): boolean {
  if (!challenge?.expires_at) return false;
  const expiresAt = Date.parse(challenge.expires_at);
  if (Number.isNaN(expiresAt)) return false;
  return Date.now() >= expiresAt;
}

export function LoginPage() {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const [challenge, setChallenge] = useState<TelegramLoginStart | null>(null);
  const [qrDataUrl, setQrDataUrl] = useState<string | null>(null);
  const [timedOut, setTimedOut] = useState(false);

  const startLogin = useMutation({
    mutationFn: api.startLogin,
    onSuccess: async (data) => {
      setTimedOut(false);
      setChallenge(data);
      setQrDataUrl(
        await QRCode.toDataURL(data.bot_url, {
          margin: 1,
          width: 360,
          color: { dark: "#0b0718", light: "#ffffff" },
        }),
      );
    },
    onError: (error: Error) => toast(error.message, "error"),
  });

  useEffect(() => {
    startLogin.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!challenge?.expires_at || timedOut) return;
    const expiresAt = Date.parse(challenge.expires_at);
    if (Number.isNaN(expiresAt)) return;
    const delay = Math.max(0, expiresAt - Date.now());
    const timer = window.setTimeout(() => setTimedOut(true), delay);
    return () => window.clearTimeout(timer);
  }, [challenge?.expires_at, challenge?.code, timedOut]);

  const waiting = Boolean(challenge) && !timedOut;

  const { data: status } = useQuery({
    queryKey: ["login-status", challenge?.code],
    queryFn: () => api.loginStatus(challenge!.code),
    enabled: waiting,
    refetchInterval: (query) => {
      if (!waiting) return false;
      const current = query.state.data?.status;
      if (current === "pending" || !current) return 2000;
      return false;
    },
  });

  useEffect(() => {
    if (status?.status === "completed") {
      login();
      toast("Вход выполнен — добро пожаловать!");
      navigate("/app", { replace: true });
    }
  }, [status?.status, login, navigate, toast]);

  useEffect(() => {
    if (status?.status !== "consumed") return;
    toast("Этот код входа уже использован. Начните вход заново.", "error");
    startLogin.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status?.status, challenge?.code]);

  useEffect(() => {
    if (status?.status === "expired" || isChallengeTimedOut(challenge)) {
      setTimedOut(true);
    }
  }, [status?.status, challenge]);

  if (isAuthenticated) return <Navigate to="/app" replace />;

  const expired = timedOut || status?.status === "expired";

  const restart = () => {
    setChallenge(null);
    setQrDataUrl(null);
    setTimedOut(false);
    startLogin.mutate();
  };

  return (
    <PageTransition>
      <div className="mx-auto max-w-xl pt-14 pb-20 text-center sm:pt-20">
        <span className="chip mx-auto">
          <ShieldCheck className="size-3.5 text-glow-cyan" />
          Вход только через Telegram
        </span>

        <h1 className="font-display mt-6 text-3xl tracking-tight sm:text-4xl">
          Подтвердите вход в <span className="text-gradient">боте</span>
        </h1>
        <p className="mx-auto mt-4 max-w-md text-sm leading-relaxed text-slate-600">
          Отсканируйте код или откройте бота — он попросит нажать «Start». Пароли и почта
          не нужны.
        </p>

        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass mt-10 p-6 sm:p-8"
        >
          {startLogin.isPending && <Spinner label="Готовим код входа…" className="py-16" />}

          {challenge && !expired && (
            <>
              <div className="mx-auto w-fit rounded-3xl bg-white p-3 shadow-2xl shadow-glow-violet/20">
                {qrDataUrl ? (
                  <img src={qrDataUrl} alt="QR-код для входа" className="size-56" />
                ) : (
                  <div className="size-56 animate-pulse rounded-xl bg-slate-200" />
                )}
              </div>

              <a
                href={challenge.bot_url}
                target="_blank"
                rel="noreferrer"
                className="btn-primary mt-8 w-full py-3.5 text-base"
              >
                <TelegramIcon className="size-5" />
                Открыть Telegram
              </a>

              <div className="mt-6 flex items-center justify-center gap-2 text-xs font-medium text-slate-600">
                <span className="size-2 animate-pulse rounded-full bg-glow-cyan" />
                Ждём подтверждения в боте…
              </div>
            </>
          )}

          {expired && (
            <div className="py-10">
              <p className="text-sm text-slate-600">
                Время кода истекло или бот не успел подтвердить вход. Запросите новый код и
                откройте свежую ссылку из Telegram.
              </p>
              <button type="button" className="btn-ghost mt-6" onClick={restart}>
                <RefreshCw className="size-4" />
                Новый код
              </button>
            </div>
          )}
        </motion.div>
      </div>
    </PageTransition>
  );
}
