# Getting started

С нуля до первого бокса на локальном стенде.

## 1. Требования

- Docker + Docker Compose
- (опционально) [uv](https://docs.astral.sh/uv/) и Node.js — только для разработки без полного compose
- Telegram-бот: токен от [@BotFather](https://t.me/BotFather) для логина

## 2. Env

Скопируйте пример и при необходимости заполните секреты:

```bash
cp docker/app/.env.example docker/app/.env
# также нужны docker/bot/.env, docker/db/.env, docker/minio/.env, docker/nginx/.env
```

Минимум для логина через Telegram:

| Переменная | Где | Зачем |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | `docker/app/.env` и `docker/bot/.env` | API Telegram |
| `TELEGRAM_BOT_USERNAME` | оба | deep-link / QR на `/login` |
| `BOT_API_SECRET` | оба, **одинаковый** | бот → `POST /api/auth/telegram/webhook` |
| `JWT_SECRET` | `docker/app/.env` | cookies сессии |

Полный список: [Env reference](env.md).

## 3. Запуск

```bash
docker compose up --build
```

Откройте http://localhost:8080

При старте API: ожидание Postgres → миграции Alembic → `python -m app.init_data` → uvicorn.

Полезные URL:

| Что | URL |
|---|---|
| Приложение | http://localhost:8080 |
| Swagger | http://localhost:8080/api/docs |
| Mailpit | http://localhost:8025 |

## 4. Первый логин

1. Откройте http://localhost:8080/login (или «Войти» на лендинге).
2. Отсканируйте QR или нажмите «Открыть Telegram».
3. В боте нажмите **Start** / подтвердите вход.
4. Фронт получит cookies (`access_token` / `refresh_token`) и попадёт на `/app`.

Без токена бота логин не завершится — challenge так и останется в статусе ожидания.

## 5. Создать бокс

1. На дашборде `/app` → **+ Новый бокс** (`/app/boxes/new`).
2. Шаги wizard: оформление → детали → содержимое (медиа) → публикация → сертификат.
3. **Опубликовать** — бокс получит `public_slug` и ссылку вида `/b/{slug}`.
4. Откройте публичную ссылку в инкогнито как получатель.

Для загрузки медиа нужны здоровые MinIO и API (`docker compose ps`).

## 6. Дальше

- [Экраны](screens.md) — как выглядит UI
- [Потоки](flows.md) — login, checkout, publish
- [Карта HTTP API](http-api.md)
- [Архитектура](architecture.md)
