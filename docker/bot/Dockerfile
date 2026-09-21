# Telegram bot (aiogram long polling → HTTP API). Build context: repo root.
FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY bot/pyproject.toml bot/uv.lock ./
RUN uv sync --frozen --no-dev

COPY bot ./bot

CMD ["python", "-m", "bot"]
