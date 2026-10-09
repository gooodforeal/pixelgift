# Pixelgift

Документация backend и веб-клиента Pixelgift (FastAPI + React).

## Разделы

- [Getting started](getting-started.md) — env → compose → логин → первый бокс
- [Архитектура](architecture.md) — слои backend
- [Потоки](flows.md) — Telegram-логин, YooKassa, публикация бокса
- [Карта HTTP API](http-api.md) — домены и основные эндпоинты
- [Env reference](env.md) — переменные окружения
- [Экраны](screens.md) — скриншоты UI
- [API Reference](reference/app/index.md) — автоген из исходников `app/`

## Локальный просмотр

```bash
uv sync --group dev
uv run mkdocs serve
```

Сайт собирается в `site/` и публикуется на GitHub Pages при push в `main`.
