# Env reference

Источник правды в коде: [`app/settings.py`](https://github.com/gooodforeal/pixelgift/blob/main/app/settings.py)  
Пример для Docker: [`docker/app/.env.example`](https://github.com/gooodforeal/pixelgift/blob/main/docker/app/.env.example)

Имена в окружении — **UPPER_SNAKE** (Pydantic Settings).  
Колонка **Обязательно**: нужно ли задавать явно для полноценного локального стенда с логином и оплатой (у многих полей есть dev-дефолты).

## База и хранилище

| Переменная | Дефолт (код) | Обязательно | Зачем |
|---|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/pixelgift` | да (в Docker — хост `db`) | Postgres async |
| `REDIS_URL` | `redis://localhost:6379/0` | да для worker | Taskiq / очереди |
| `MINIO_ENDPOINT` | `http://localhost:9000` | да | S3-совместимое хранилище |
| `MINIO_ACCESS_KEY` | `minioadmin` | да | ключ MinIO |
| `MINIO_SECRET_KEY` | `minioadmin` | да | секрет MinIO |
| `MINIO_BUCKET` | `pixelgift` | да | бакет медиа/аватаров |
| `MINIO_REGION` | `us-east-1` | нет | регион S3 API |

## Публичные URL и CORS

| Переменная | Дефолт | Обязательно | Зачем |
|---|---|---|---|
| `API_BASE_URL` | `http://localhost:8080/api` | да для фронта | базовый URL API в браузере |
| `PUBLIC_WEB_URL` | `http://localhost:8080` | да | ссылки на боксы / редиректы |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:8080` | да | разрешённые origins (через запятую) |

## Telegram и бот

| Переменная | Дефолт | Обязательно | Зачем |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | `""` | да для логина | Bot API |
| `TELEGRAM_BOT_USERNAME` | `""` | да для логина | deep-link / QR |
| `SUPPORT_TELEGRAM_URL` | `https://t.me/pixelgift_auth_bot` | нет | ссылка поддержки в UI |
| `BOT_API_SECRET` | `dev-bot-api-secret` | да | секрет вызовов бота → API |

Токен и username также нужны в `docker/bot/.env`. `BOT_API_SECRET` должен совпадать с API.

## JWT и cookies

| Переменная | Дефолт | Обязательно | Зачем |
|---|---|---|---|
| `JWT_SECRET` | `dev-change-me-...` | да (смените в проде) | подпись JWT |
| `JWT_ALGORITHM` | `HS256` | нет | алгоритм |
| `JWT_ACCESS_TOKEN_TTL_MINUTES` | `15` | нет | TTL access |
| `JWT_REFRESH_TOKEN_TTL_DAYS` | `30` | нет | TTL refresh |
| `COOKIE_SECURE` | `false` | в проде `true` | Secure-флаг cookies |
| `LOGIN_CHALLENGE_TTL_MINUTES` | `10` | нет | жизнь challenge логина |
| `ACCESS_COOKIE_NAME` | `access_token` | нет | имя cookie |
| `REFRESH_COOKIE_NAME` | `refresh_token` | нет | имя cookie |

## SMTP и уведомления

| Переменная | Дефолт | Обязательно | Зачем |
|---|---|---|---|
| `SMTP_HOST` | `localhost` | да для email | в Docker — `mailpit` |
| `SMTP_PORT` | `1025` | нет | порт SMTP |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | пусто | нет | auth SMTP |
| `SMTP_FROM_EMAIL` | `PixelGift <noreply@...>` | нет | From |
| `SMTP_USE_TLS` | `false` | нет | TLS |
| `NOTIFICATION_MAX_ATTEMPTS` | `2` | нет | попытки отправки job |
| `NOTIFICATION_PROCESSING_STALE_MINUTES` | `10` | нет | reclaim зависших job |

## SQLAdmin

| Переменная | Дефолт | Обязательно | Зачем |
|---|---|---|---|
| `SQLADMIN_USERNAME` | `admin` | да для `/admin` | логин SQLAdmin |
| `SQLADMIN_PASSWORD` | `admin` | да (смените) | пароль |
| `SQLADMIN_SECRET_KEY` | `dev-sqladmin-...` | да | сессии admin |
| `SQLADMIN_COOKIE_SECURE` | `false` | в проде `true` | Secure cookie |
| `SQLADMIN_COOKIE_SAMESITE` | `lax` | нет | SameSite |

## LLM (ассистент редактора)

| Переменная | Дефолт | Обязательно | Зачем |
|---|---|---|---|
| `LLM_API_KEY` | `""` | да для ассистента | ключ провайдера |
| `LLM_BASE_URL` | `https://api.openai.com/v1` | нет | OpenAI-compatible base (в `.env.example` — Groq) |
| `LLM_MODEL` | `gpt-4o-mini` | нет | модель |
| `LLM_TIMEOUT_SECONDS` | `60` | нет | таймаут |
| `LLM_ASSISTANT_MAX_MESSAGES` | `20` | нет | лимит истории |
| `LLM_PROXY_URL` | `""` | нет | HTTP(S)-прокси только для LLM |

## YooKassa

| Переменная | Дефолт | Обязательно | Зачем |
|---|---|---|---|
| `YOOKASSA_SHOP_ID` | `""` | да для оплаты | shop id |
| `YOOKASSA_SECRET_KEY` | `""` | да для оплаты | секрет |
| `YOOKASSA_RETURN_URL` | `http://localhost:8080/app/profile` | нет | return URL после оплаты |
| `YOOKASSA_TIMEOUT_SECONDS` | `30` | нет | таймаут API |

Без ключей YooKassa checkout с ненулевой суммой не создаст платёж; заказы на 0 ₽ (100% промо) могут проходить без провайдера.
