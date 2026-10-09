# Потоки

Ключевые сценарии backend + фронт. Подробные сигнатуры — в [карте API](http-api.md) и OpenAPI.

## Логин через Telegram

```mermaid
sequenceDiagram
    autonumber
    actor U as Пользователь
    participant W as Web (/login)
    participant A as API
    participant B as Telegram-бот
    participant TG as Telegram

    U->>W: Открыть /login
    W->>A: POST /auth/telegram/start
    A-->>W: code + deep-link / QR
    W->>W: Poll GET /auth/telegram/status

    U->>TG: Открыть бота, Start
    TG->>B: Update / команда с code
    B->>A: POST /auth/telegram/webhook<br/>(BOT_API_SECRET)
    A->>A: Привязать Telegram → User,<br/>отметить challenge completed

    W->>A: GET /auth/telegram/status
    A-->>W: ready + set cookies<br/>access_token, refresh_token
    W->>W: sessionStorage authed
    W->>U: Редирект на /app
```

Кратко: браузер только создаёт challenge и ждёт; **завершает** логин бот через защищённый webhook.

## Checkout и webhook YooKassa

```mermaid
sequenceDiagram
    autonumber
    actor U as Пользователь
    participant W as Web
    participant A as API
    participant Y as YooKassa

    U->>W: Корзина → оформить
    W->>A: POST /cart/checkout<br/>(опционально promo_code)

    alt сумма после скидки = 0
        A->>A: Начислить кредиты,<br/>заказ succeeded, очистить корзину
        A-->>W: order без confirmation_url
    else сумма > 0
        A->>Y: create_payment
        Y-->>A: payment_id + confirmation_url
        A->>A: Заказ PENDING, очистить корзину
        A-->>W: order + confirmation_url
        W->>Y: Редирект на оплату
        Y->>A: POST /payments/yookassa/webhook
        A->>A: Сверить платёж → succeeded,<br/>начислить товары/кредиты
        Y-->>U: Return URL (профиль)
    end

    Note over W,A: Fallback: POST /orders/sync<br/>опрашивает pending у провайдера
```

Webhook — основной путь подтверждения; `/orders/sync` — страховка, если webhook задержался.

## Публикация бокса

```mermaid
flowchart TD
    A[POST /boxes<br/>черновик] --> B[PUT /boxes/id<br/>дизайн, детали, пароль, activates_at]
    B --> C[POST /media<br/>загрузка файлов]
    C --> D[POST /boxes/id/items<br/>привязка медиа к боксу]
    D --> E{Валидно для публикации?<br/>дизайн, items, правила domain}
    E -->|нет| B
    E -->|да| F[POST /boxes/id/publish]
    F --> G[Статус active<br/>public_slug]
    G --> H[Ссылка /b/slug]
    H --> I[Получатель: GET /b/slug]
    I --> J{Нужен unlock?<br/>пароль / время}
    J -->|да| K[POST /b/slug/unlock]
    J -->|нет| L[Контент<br/>GET .../items/.../content]
    K --> L
    G --> M[GET /boxes/id/certificate.pdf]
```

Владелец правит бокс только до/в рамках правил `BoxNotEditableError`; после publish получатель ходит только в **public**-эндпоинты.
