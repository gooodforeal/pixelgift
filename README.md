# Pixelgift

Сервис цифровых подарочных боксов: сборка бокса (дизайн, контент, медиа), публикация по публичной ссылке, сертификат, магазин кредитов и Telegram-аутентификация.

## Возможности

- Редактор бокса с дизайнами, карточками контента и медиа
- Публичная страница получателя (slug, пароль, отложенная активация)
- PDF-сертификат с QR
- Каталог товаров / корзина / оплата через YooKassa, баланс и промокоды
- AI-ассистент в редакторе (OpenAI-compatible LLM)
- Логин через Telegram-бот + JWT (access/refresh cookies)
- Тикеты поддержки, админка (SQLAdmin + admin UI во фронте)
- Фоновые уведомления (email / Telegram) через Taskiq + Redis

## Стек

| Часть | Технологии |
|---|---|
| API | Python 3.11+, FastAPI, SQLAlchemy 2, Alembic, Pydantic Settings |
| Фронт | React 19, Vite, TypeScript, TanStack Query, Tailwind 4 |
| Бот | aiogram 3 → HTTP API |
| Инфра | PostgreSQL, Redis, MinIO (S3), Mailpit, Nginx |
| Очереди | Taskiq (worker + scheduler) |
| Платежи | YooKassa |
| Docs | MkDocs Material + mkdocstrings → [GitHub Pages](https://gooodforeal.github.io/pixelgift/) |

Backend построен по слоям (clean / hexagonal): `domain` ← `application` ← `presentation` / `infrastructure`. Подробнее: [docs/architecture.md](docs/architecture.md).

## Структура репозитория

```text
app/                 # FastAPI backend
bot/                 # Telegram-бот (отдельный пакет)
front/               # React SPA
migrations/          # Alembic
docker/              # Dockerfile’ы и env для compose
docs/                # Исходники MkDocs
tests/               # pytest
docker-compose.yaml  # Полный локальный стенд
```

## Быстрый старт (Docker)

Нужны Docker и Docker Compose. Env-файлы лежат в `docker/*/` (для API есть `docker/app/.env.example`).

```bash
# Скопируйте и заполните env при необходимости
cp docker/app/.env.example docker/app/.env   # если .env ещё нет

docker compose up --build
```

Сервисы: `db`, `redis`, `minio`, `mailpit`, `app`, `taskiq_worker`, `taskiq_scheduler`, `bot`, `front`, `nginx`.

При старте API: ожидание Postgres → `alembic upgrade head` → `python -m app.init_data` → uvicorn.

### URL после `compose up`

| Сервис | URL |
|---|---|
| Приложение (edge nginx) | http://localhost:8080 |
| Health API | http://localhost:8080/health (через nginx) / внутри контейнера `:8000` |
| Swagger / ReDoc | http://localhost:8080/docs , `/redoc` |
| Mailpit UI | http://localhost:8025 |
| Postgres | `localhost:5432` |
| Redis | `localhost:6379` |

Точные пути API зависят от nginx; публичный веб — `PUBLIC_WEB_URL` (по умолчанию `http://localhost:8080`).

## Локальная разработка без полного compose

### Backend

```bash
# Инфра: хотя бы Postgres (+ Redis/MinIO по необходимости)
docker compose up -d db redis minio mailpit

uv sync --group dev
# Настройки: app/.env или переменные окружения (см. app/settings.py)
uv run alembic upgrade head
uv run python -m app.init_data
uv run uvicorn app.main:app --reload --port 8000
```

Тесты:

```bash
uv run pytest
```

### Frontend

```bash
cd front
npm install
npm run dev      # Vite, обычно http://localhost:5173
```

Убедитесь, что `CORS_ORIGINS` на API включает origin фронта.

### Telegram-бот

```bash
cd bot
uv sync
# docker/bot/.env или bot settings: токен, API base URL, bot secret
uv run python -m bot
```

### Документация кода (MkDocs)

```bash
uv sync --group dev
uv run mkdocs serve
# http://127.0.0.1:8000
```

Сборка: `uv run mkdocs build`. Публикация на Pages — workflow `.github/workflows/docs.yml` при push в `main`.  
Онлайн: https://gooodforeal.github.io/pixelgift/

## Конфигурация

Основные переменные задаются через env (см. `app/settings.py` и `docker/app/.env.example`):

- `DATABASE_URL`, `REDIS_URL`, MinIO (`MINIO_*`)
- `JWT_*`, cookie / CORS / `PUBLIC_WEB_URL`, `API_BASE_URL`
- `TELEGRAM_BOT_*`, `BOT_API_SECRET`
- `SMTP_*` (локально — Mailpit)
- `LLM_*` — ассистент в редакторе
- `YOOKASSA_*` — платежи
- `SQLADMIN_*` — админка SQLAdmin

Секреты и токены в репозиторий не коммитьте.

## Документация

- Getting started: [docs/getting-started.md](docs/getting-started.md)
- Архитектура: [docs/architecture.md](docs/architecture.md)
- Потоки (Mermaid): [docs/flows.md](docs/flows.md)
- Карта HTTP API: [docs/http-api.md](docs/http-api.md)
- Env reference: [docs/env.md](docs/env.md)
- Экраны UI: [docs/screens.md](docs/screens.md)
- API Reference: https://gooodforeal.github.io/pixelgift/reference/
- Сайт docs: https://gooodforeal.github.io/pixelgift/
