import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Send, X } from "lucide-react";

import { api } from "../lib/api";
import { getOrCreateAssistantThreadId } from "../lib/assistantThread";
import type {
  AssistantHistoryMessage,
  Box,
  BoxEditorFormSnapshot,
  BoxWizardAssistantStep,
} from "../lib/types";
import { GiftiAvatar } from "./GiftiAvatar";
import { Spinner } from "./Spinner";
import { useToast } from "./Toast";
import type { BoxWizardStepId } from "./BoxWizardProgress";

interface BoxAssistantChatProps {
  box?: Box;
  step: BoxWizardStepId;
  /** Pre-create session thread; ignored once box exists. */
  threadId?: string | null;
  form: {
    design_id: string;
    title: string;
    recipient_name: string;
    recipient_email: string;
    unlock_password: string;
    activates_at_local: string;
    message: string;
    preview_title: string;
  };
  timezone?: string;
}

const ASSISTANT_NAME = "Гифти";

const WELCOME_MESSAGE: AssistantHistoryMessage = {
  role: "assistant",
  content:
    "Привет! Я Гифти — помогу собрать бокс: подскажу шаги, типы карточек и что ещё не заполнено.",
};

const STEP_CHIPS: Record<BoxWizardAssistantStep, string[]> = {
  design: ["Как выбрать тему?", "Что даёт оформление?"],
  details: ["Что обязательно заполнить?", "Какой пароль подойдёт?"],
  content: [
    "Какие карточки добавить?",
    "Чем отличается question от text?",
    "Сколько карточек ещё можно?",
  ],
  publish: ["Готов ли бокс к публикации?", "Что будет после publish?"],
  certificate: ["Зачем сертификат?", "Где пароль и QR?"],
};

function toFormSnapshot(
  form: BoxAssistantChatProps["form"],
  timezone?: string,
): BoxEditorFormSnapshot {
  return {
    design_id: form.design_id || null,
    title: form.title || null,
    recipient_name: form.recipient_name || null,
    recipient_email: form.recipient_email || null,
    unlock_password_set: Boolean(form.unlock_password.trim()),
    activates_at: form.activates_at_local || null,
    timezone: timezone ?? null,
    message: form.message || null,
    preview_title: form.preview_title || null,
  };
}

function AssistantMessageRow({
  children,
  showName = true,
}: {
  children: ReactNode;
  showName?: boolean;
}) {
  return (
    <div className="box-assistant__row box-assistant__row--assistant">
      <GiftiAvatar className="box-assistant__avatar" />
      <div className="box-assistant__row-body">
        {showName ? (
          <p className="box-assistant__name">{ASSISTANT_NAME}</p>
        ) : null}
        {children}
      </div>
    </div>
  );
}

export function BoxAssistantChat({
  box,
  step,
  threadId: threadIdProp,
  form,
  timezone,
}: BoxAssistantChatProps) {
  const toast = useToast();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const fallbackThreadIdRef = useRef(getOrCreateAssistantThreadId());
  const threadId = box?.id
    ? null
    : (threadIdProp ?? fallbackThreadIdRef.current);
  const [messages, setMessages] = useState<AssistantHistoryMessage[]>([
    WELCOME_MESSAGE,
  ]);
  const listRef = useRef<HTMLDivElement>(null);
  const chips = useMemo(() => STEP_CHIPS[step] ?? [], [step]);
  const threadKey = box?.id ?? threadId ?? "none";

  useEffect(() => {
    let cancelled = false;

    async function loadHistory() {
      setHistoryLoading(true);
      try {
        const result = await api.boxAssistantHistory({
          boxId: box?.id ?? null,
          threadId,
        });
        if (cancelled) return;
        setMessages(
          result.messages.length > 0 ? result.messages : [WELCOME_MESSAGE],
        );
      } catch {
        if (cancelled) return;
        setMessages([WELCOME_MESSAGE]);
      } finally {
        if (!cancelled) setHistoryLoading(false);
      }
    }

    void loadHistory();
    return () => {
      cancelled = true;
    };
  }, [threadKey, box?.id, threadId]);

  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const node = listRef.current;
    if (!node) return;
    node.scrollTop = node.scrollHeight;
  }, [messages, open, pending, historyLoading]);

  async function sendMessage(raw: string) {
    const message = raw.trim();
    if (!message || pending || historyLoading) return;

    setMessages((current) => [...current, { role: "user", content: message }]);
    setInput("");
    setPending(true);

    try {
      const result = await api.boxAssistantChat({
        message,
        step,
        box_id: box?.id ?? null,
        thread_id: threadId,
        form: toFormSnapshot(form, timezone ?? box?.timezone),
      });
      setMessages((current) => [
        ...current,
        { role: "assistant", content: result.reply },
      ]);
    } catch {
      toast("Гифти сейчас недоступен. Попробуйте позже", "error");
      setMessages((current) => current.slice(0, -1));
      setInput(message);
    } finally {
      setPending(false);
    }
  }

  if (typeof document === "undefined") return null;

  return createPortal(
    <>
      <button
        type="button"
        className="box-assistant__fab"
        aria-label={`Открыть чат с ${ASSISTANT_NAME}`}
        onClick={() => setOpen(true)}
      >
        <GiftiAvatar className="box-assistant__fab-avatar" />
        <span className="box-assistant__fab-label">{ASSISTANT_NAME}</span>
      </button>

      <AnimatePresence>
        {open ? (
          <>
            <motion.button
              key="box-assistant-backdrop"
              type="button"
              aria-label={`Закрыть чат с ${ASSISTANT_NAME}`}
              className="box-assistant__backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.18 }}
              onClick={() => setOpen(false)}
            />

            <motion.aside
              key="box-assistant-panel"
              role="dialog"
              aria-modal="true"
              aria-label={`${ASSISTANT_NAME} — помощник создания бокса`}
              className="box-assistant glass"
              initial={{ opacity: 0, x: 28 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
            >
              <header className="box-assistant__header">
                <div className="box-assistant__header-identity">
                  <GiftiAvatar className="box-assistant__header-avatar" />
                  <div className="min-w-0">
                    <h2 className="box-assistant__title">{ASSISTANT_NAME}</h2>
                    <p className="box-assistant__kicker">Помощник PixelGift</p>
                  </div>
                </div>
                <button
                  type="button"
                  className="btn-ghost size-10 px-0!"
                  aria-label="Закрыть"
                  onClick={() => setOpen(false)}
                >
                  <X className="size-4" />
                </button>
              </header>

              <div ref={listRef} className="box-assistant__messages">
                {messages.map((item, index) =>
                  item.role === "assistant" ? (
                    <AssistantMessageRow
                      key={`${item.role}-${index}`}
                      showName={
                        index === 0 || messages[index - 1]?.role !== "assistant"
                      }
                    >
                      <div className="box-assistant__bubble box-assistant__bubble--assistant">
                        {item.content}
                      </div>
                    </AssistantMessageRow>
                  ) : (
                    <div
                      key={`${item.role}-${index}`}
                      className="box-assistant__row box-assistant__row--user"
                    >
                      <div className="box-assistant__bubble box-assistant__bubble--user">
                        {item.content}
                      </div>
                    </div>
                  ),
                )}
                {historyLoading ? (
                  <AssistantMessageRow showName={false}>
                    <div className="box-assistant__bubble box-assistant__bubble--assistant">
                      <Spinner label="Загружаем историю…" className="py-1" />
                    </div>
                  </AssistantMessageRow>
                ) : null}
                {pending ? (
                  <AssistantMessageRow showName={false}>
                    <div className="box-assistant__bubble box-assistant__bubble--assistant">
                      <Spinner label="Гифти думает…" className="py-1" />
                    </div>
                  </AssistantMessageRow>
                ) : null}
              </div>

              <div className="box-assistant__chips">
                {chips.map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    className="box-assistant__chip"
                    disabled={pending || historyLoading}
                    onClick={() => {
                      void sendMessage(chip);
                    }}
                  >
                    {chip}
                  </button>
                ))}
              </div>

              <form
                className="box-assistant__composer"
                onSubmit={(event) => {
                  event.preventDefault();
                  void sendMessage(input);
                }}
              >
                <input
                  className="field box-assistant__input"
                  value={input}
                  disabled={pending || historyLoading}
                  placeholder={`Спросите Гифти про шаг или карточки…`}
                  onChange={(event) => setInput(event.target.value)}
                />
                <button
                  type="submit"
                  className="btn-primary size-11 shrink-0 px-0!"
                  disabled={pending || historyLoading || !input.trim()}
                  aria-label="Отправить"
                >
                  <Send className="size-4" />
                </button>
              </form>
            </motion.aside>
          </>
        ) : null}
      </AnimatePresence>
    </>,
    document.body,
  );
}
