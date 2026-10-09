# Карта HTTP API

Базовый URL через nginx: **`http://localhost:8080/api`**  
(префикс `/api/` снимается при проксировании на FastAPI.)

Интерактивная схема: [Swagger UI](http://localhost:8080/api/docs) · [ReDoc](http://localhost:8080/api/redoc)  
(у запущенного стенда; пути относительно API upstream — `/docs`, `/redoc`.)

Аутентификация браузера: HttpOnly cookies `access_token` / `refresh_token` (`credentials: include`).  
Бот → API: заголовок с `BOT_API_SECRET` на webhook логина.

## Домены

| Домен | Prefix / пути | Назначение | Auth |
|---|---|---|---|
| **health** | `GET /health` | Liveness | нет |
| **auth** | `/auth/*`, `GET /users/{id}/avatar` | Telegram-логин, refresh, me, logout | смешанный |
| **designs** | `/designs` | Каталог тем, ассеты, рейтинг | публичный список; рейтинг — юзер |
| **boxes** | `/boxes` | CRUD бокса, items, publish/archive, сертификат | владелец |
| **public** | `/b/{slug}` | Публичный бокс, unlock, контент | slug (+ пароль) |
| **media** | `/media` | Загрузка и отдача файлов | владелец |
| **commerce** | `/products`, `/cart`, `/orders`, `/balances`, `/payments/...` | Каталог, корзина, оплата, баланс | юзер; webhook — YooKassa |
| **assistant** | `/assistant` | Чат ассистента в редакторе | юзер |
| **support** | `/support` | Конфиг и создание тикета | смешанный |
| **admin-*** | `/admin/products`, `/admin/promo-codes`, `/admin/designs`, `/admin/support` | Админские операции | `is_admin` |

Отдельно (не под `/api` в swagger-смысле edge): **SQLAdmin** на `/admin` (базовый auth из `SQLADMIN_*`).

## Auth

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/auth/telegram/start` | Создать login challenge (код + deep-link) |
| `GET` | `/auth/telegram/status` | Polling статуса challenge |
| `POST` | `/auth/telegram/webhook` | Бот завершает логин (`BOT_API_SECRET`) |
| `POST` | `/auth/refresh` | Обновить access по refresh-cookie |
| `GET` / `PATCH` | `/auth/me` | Текущий пользователь |
| `POST` | `/auth/logout` | Выход |
| `GET` | `/users/{user_id}/avatar` | Аватар |

## Boxes

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/boxes` | Создать бокс |
| `GET` | `/boxes` | Список боксов владельца |
| `GET` | `/boxes/opens` | Статистика открытий за месяц |
| `GET` / `PUT` | `/boxes/{id}` | Получить / обновить |
| `POST` | `/boxes/{id}/publish` | Опубликовать |
| `POST` | `/boxes/{id}/archive` · `/unarchive` | Архив |
| `POST` / `PATCH` / `DELETE` | `/boxes/{id}/items...` | Элементы контента |
| `PUT` | `/boxes/{id}/items/reorder` | Порядок |
| `GET` | `/boxes/{id}/certificate.pdf` | PDF-сертификат |

## Public

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/b/{public_slug}` | Метаданные публичного бокса |
| `POST` | `/b/{public_slug}/unlock` | Разблокировка (пароль / активация) |
| `GET` | `/b/{public_slug}/items/{item_id}/content` | Контент элемента |

## Commerce

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/products` | Публичный каталог |
| `GET` / `POST` / `PATCH` / `DELETE` | `/cart`, `/cart/items...` | Корзина |
| `POST` | `/cart/checkout` | Заказ + YooKassa confirmation URL |
| `POST` | `/orders/sync` | Fallback-синхронизация pending-заказов |
| `GET` | `/orders`, `/orders/{id}` | История заказов |
| `GET` | `/balances`, `/balance-logs` | Баланс и лог |
| `POST` | `/payments/yookassa/webhook` | Webhook оплаты |

## Media · Support · Assistant · Admin

| Домен | Ключевые пути |
|---|---|
| **media** | `POST /media`, `GET /media/{id}/content` |
| **support** | `GET /support/config`, `POST /support` (multipart) |
| **assistant** | `GET /assistant/box-editor/history`, `POST /assistant/box-editor` |
| **admin** | `/admin/products`, `/admin/promo-codes`, `/admin/designs`, `/admin/support` |

Точные схемы тел и коды ответов — в OpenAPI (`/docs`).  
Код роутеров: `app/presentation/routers/`.
