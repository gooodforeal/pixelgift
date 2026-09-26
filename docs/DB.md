# Схема базы данных

PostgreSQL. Идентификаторы сущностей — `UUID`.

## Обзор

| Таблица | Назначение |
|---------|------------|
| `users` | Создатели боксов (профиль по Telegram) |
| `telegram_login_challenges` | Одноразовые коды входа через бота |
| `user_sessions` | Refresh-сессии (опционально для MVP) |
| `box_designs` | Каталог дизайнов бокса |
| `boxes` | Виртуальный бокс, ссылка, активация, превью |
| `media_files` | Метаданные файлов в object storage |
| `box_items` | Элементы контента внутри бокса |
| `products` | Каталог товаров (`box_credit` и др.): название, описание, цена |
| `carts` / `cart_items` | Корзина пользователя |
| `orders` / `order_items` | Заказы и позиции для ЮKassa |
| `promo_codes` | Промокоды (скидка %, TTL, usage_count) |
| `user_balances` | Остатки кредитов по товарам |
| `user_balance_logs` | Журнал движений баланса |

Связи:

- `users` → `boxes`, `media_files`, `user_sessions`, `telegram_login_challenges`, `carts`, `orders`, `user_balances`, `user_balance_logs`, `promo_codes` (created_by)
- `box_designs` → `boxes`
- `boxes` → `box_items` → `media_files`
- `products` → `cart_items`, `order_items`, `user_balances`, `user_balance_logs`
- `carts` → `cart_items`
- `orders` → `order_items`, опционально `promo_codes`

Публичный просмотр бокса по `public_slug` **не требует** записи в `users`.

---

## `users`

Пользователи, которые создают и редактируют боксы. Создаются/обновляются при успешном входе через Telegram-бота.

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| `id` | `UUID` | PK | Внутренний идентификатор |
| `telegram_id` | `BIGINT` | NOT NULL, UNIQUE | ID пользователя в Telegram |
| `username` | `VARCHAR(64)` | NULL | `@username` |
| `first_name` | `VARCHAR(128)` | NOT NULL | Имя из профиля |
| `last_name` | `VARCHAR(128)` | NULL | |
| `language_code` | `VARCHAR(10)` | NULL | Язык UI (`ru`, `en`, …) |
| `photo_url` | `TEXT` | NULL | URL аватара |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | Блокировка аккаунта |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | |
| `last_seen_at` | `TIMESTAMPTZ` | NULL | Последний успешный вход |

**Индексы:** `UNIQUE (telegram_id)`.

---

## `telegram_login_challenges`

Одноразовые коды для сценария «сайт → бот → сайт». Подробности потока — в [AUTH.md](./AUTH.md).

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| `id` | `UUID` | PK | |
| `code` | `VARCHAR(64)` | NOT NULL, UNIQUE | Payload в `?start=login_<code>` |
| `status` | `VARCHAR(16)` | NOT NULL | `pending`, `completed`, `expired` |
| `telegram_id` | `BIGINT` | NULL | Заполняется при обработке `/start` в боте |
| `user_id` | `UUID` | NULL, FK → `users.id` | После upsert пользователя |
| `expires_at` | `TIMESTAMPTZ` | NOT NULL | TTL (обычно 5–10 минут) |
| `completed_at` | `TIMESTAMPTZ` | NULL | Момент подтверждения в боте |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | |
| `client_ip_hash` | `VARCHAR(64)` | NULL | Опционально, защита от злоупотреблений |

**Индексы:** `UNIQUE (code)`; `(status, expires_at)` — очистка просроченных записей.

Код после `completed` не переиспользуется.

---

## `user_sessions`

Опционально. Нужна, если используются refresh-токены и явный logout. Для MVP достаточно короткоживущего или долгоживущего JWT без таблицы.

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| `id` | `UUID` | PK | |
| `user_id` | `UUID` | NOT NULL, FK → `users.id` ON DELETE CASCADE | |
| `refresh_token_hash` | `VARCHAR(128)` | NOT NULL, UNIQUE | Хеш refresh-токена |
| `expires_at` | `TIMESTAMPTZ` | NOT NULL | |
| `revoked_at` | `TIMESTAMPTZ` | NULL | Отзыв сессии |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | |
| `user_agent` | `VARCHAR(512)` | NULL | |
| `ip_hash` | `VARCHAR(64)` | NULL | |

**Индексы:** `(user_id)`; `(expires_at)` для активных сессий.

---

## `box_designs`

Справочник шаблонов оформления бокса.

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| `id` | `UUID` | PK | |
| `code` | `VARCHAR(64)` | NOT NULL, UNIQUE | Стабильный ключ (`romantic_red`, …) |
| `name` | `VARCHAR(128)` | NOT NULL | Название в UI |
| `description` | `TEXT` | NULL | |
| `preview_image_url` | `TEXT` | NOT NULL | Превью в каталоге дизайнов |
| `theme_config` | `JSONB` | NOT NULL, default `{}` | Цвета, шрифты, анимации |
| `is_active` | `BOOLEAN` | NOT NULL, default `true` | Показывать в выборе |
| `sort_order` | `INTEGER` | NOT NULL, `> 0` | Порядок в списке |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | |

---

## `boxes`

Один виртуальный подарочный бокс. Уникальная ссылка для получателя — `public_slug` (`/b/{slug}`).

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| `id` | `UUID` | PK | |
| `owner_id` | `UUID` | NOT NULL, FK → `users.id` | Создатель |
| `design_id` | `UUID` | NOT NULL, FK → `box_designs.id` | Выбранный дизайн |
| `public_slug` | `VARCHAR(32)` | NOT NULL, UNIQUE | Публичный slug ссылки |
| `title` | `VARCHAR(256)` | NOT NULL | Заголовок для получателя |
| `recipient_name` | `VARCHAR(128)` | NOT NULL | Имя получателя |
| `message` | `TEXT` | NULL | Текст внутри открытого бокса |
| `preview_title` | `VARCHAR(256)` | NULL | Текст на экране до активации |
| `preview_image_url` | `TEXT` | NULL | Изображение превью до активации |
| `activates_at` | `TIMESTAMPTZ` | NOT NULL | Дата и время открытия контента (UTC) |
| `timezone` | `VARCHAR(64)` | NOT NULL, default `UTC` | IANA-зона для таймера в UI |
| `status` | `VARCHAR(16)` | NOT NULL | `draft`, `scheduled`, `active`, `archived` |
| `published_at` | `TIMESTAMPTZ` | NULL | Момент публикации создателем |
| `first_opened_at` | `TIMESTAMPTZ` | NULL | Первый заход получателя по ссылке |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | |

**Статусы:**

- `draft` — черновик, публичная ссылка может быть недоступна.
- `scheduled` — опубликован, контент скрыт до `activates_at`.
- `active` — контент доступен (`now >= activates_at`).
- `archived` — скрыт или удалён создателем.

**Индексы:** `UNIQUE (public_slug)`; `(owner_id, created_at DESC)`; `(status, activates_at)`.

**Логика показа:**

- До `activates_at`: API отдаёт только превью (`preview_title`, `preview_image_url`, таймер), без `box_items`.
- После активации: полный контент (`message`, `box_items`, signed URL к файлам).

---

## `media_files`

Бинарники хранятся в object storage (S3/MinIO); в БД — только метаданные.

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| `id` | `UUID` | PK | |
| `owner_id` | `UUID` | NOT NULL, FK → `users.id` | Кто загрузил |
| `storage_key` | `TEXT` | NOT NULL | Путь в bucket |
| `original_filename` | `VARCHAR(512)` | NULL | Исходное имя файла |
| `mime_type` | `VARCHAR(128)` | NOT NULL | |
| `media_kind` | `VARCHAR(16)` | NOT NULL | `image`, `gif`, `video`, `audio`, `voice` |
| `size_bytes` | `BIGINT` | NOT NULL | |
| `duration_ms` | `INTEGER` | NULL | Видео / аудио |
| `width` | `INTEGER` | NULL | |
| `height` | `INTEGER` | NULL | |
| `checksum_sha256` | `CHAR(64)` | NULL | Целостность / дедуп |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | |

**Индексы:** `(owner_id, created_at DESC)`.

---

## `box_items`

Элементы контента в боксе (фото, гифки, видео, голосовые и т.д.) с порядком отображения.

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| `id` | `UUID` | PK | |
| `box_id` | `UUID` | NOT NULL, FK → `boxes.id` ON DELETE CASCADE | |
| `media_file_id` | `UUID` | NOT NULL, FK → `media_files.id` | |
| `item_type` | `VARCHAR(16)` | NOT NULL | `image`, `gif`, `video`, `voice` |
| `sort_order` | `INTEGER` | NOT NULL, `> 0` | Порядок в боксе (1, 2, 3, …) |
| `caption` | `TEXT` | NULL | Подпись к элементу |
| `metadata` | `JSONB` | NOT NULL, default `{}` | Poster для видео, waveform и т.п. |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | |

**Индексы:** `UNIQUE (box_id, sort_order)`.

---

## `products`

Каталог продаваемых единиц. Seed: `sku=box_credit`, `kind=credit`, цена в копейках.

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| `id` | `UUID` | PK | |
| `sku` | `VARCHAR(64)` | NOT NULL, UNIQUE | Код товара |
| `name` | `VARCHAR(128)` | NOT NULL | |
| `description` | `TEXT` | NOT NULL | Описание для витрины |
| `image_urls` | `JSONB` | NOT NULL | Массив URL фото (0–5) |
| `kind` | `VARCHAR(32)` | NOT NULL | `credit` и др. |
| `unit_price` | `INTEGER` | NOT NULL | Цена в копейках |
| `currency` | `VARCHAR(8)` | NOT NULL | `RUB` |
| `is_active` | `BOOLEAN` | NOT NULL | |

## `carts` / `cart_items`

Одна корзина на пользователя (`carts.user_id` UNIQUE). Позиции: UNIQUE (`cart_id`, `product_id`), `quantity ≥ 1`.

## `orders` / `order_items`

Заказ после checkout: статус `pending` / `succeeded` / `canceled`, сумма, `provider=yookassa`, `provider_payment_id`, `idempotency_key`, `confirmation_url`, `paid_at`. Опционально: `promo_code_id`, `discount_percent`, `amount_before_discount`. Позиции хранят снимок `unit_price` / `amount`. При 100% промокоде заказ сразу `succeeded` без ЮKassa.

## `promo_codes`

Код 4–20 (`A–Z0–9`, UNIQUE), `discount_percent` (5–100, кратно 5), `expires_at`, `usage_count`, `is_active`, `created_by_user_id`.

## `user_balances` / `user_balance_logs`

Остаток по `(user_id, product_id)`. Журнал: `delta`, `balance_after`, `reason` (`purchase` / `consume` / …), `reference_type` + `reference_id` (unique вместе с reason). Индекс `(user_id, created_at)` для пагинации.

Поток: корзина → checkout (±промокод) → ЮKassa → webhook `succeeded` → `+quantity` на баланс (+`usage_count`); `POST /boxes` (создание) → `-1` `box_credit`.

---

## Правила доступа (уровень API)

| Ресурс | Авторизация |
|--------|-------------|
| CRUD боксов, загрузка `media_files` | JWT создателя (`users.id` в claims) |
| `GET /b/{public_slug}` | Без авторизации |
| Контент `box_items` до `activates_at` | Не отдавать (или только blurred preview) |
| `telegram_login_challenges` | Только backend и webhook бота |

---

## MVP: минимальный набор таблиц

Обязательно:

1. `users`
2. `telegram_login_challenges`
3. `box_designs`
4. `boxes`
5. `media_files`
6. `box_items`

Можно отложить: `user_sessions`.
