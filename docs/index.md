# Pixelgift

Документация backend-приложения Pixelgift (FastAPI).

## Разделы

- [Архитектура](architecture.md) — слои и поток запросов
- [API Reference](reference/app/index.md) — автоген из исходников `app/`

## Локальный просмотр

```bash
uv sync --group dev
uv run mkdocs serve
```

Сайт собирается в `site/` и публикуется на GitHub Pages при push в `main`.
