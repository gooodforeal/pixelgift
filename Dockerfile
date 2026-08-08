FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY alembic.ini ./
COPY migrations ./migrations
COPY scripts ./scripts
COPY assets ./assets
COPY src ./src
COPY bot ./bot

RUN chmod +x /app/scripts/entrypoint.sh /app/scripts/seed_static_assets.py

EXPOSE 8000

CMD ["/app/scripts/entrypoint.sh"]
