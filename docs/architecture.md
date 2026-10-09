# Архитектура

Backend организован по слоям (clean / hexagonal). Зависимости направлены внутрь: presentation и infrastructure зависят от application и domain, но не наоборот.

```text
presentation  →  application  →  domain
       ↓              ↓
 infrastructure (adapters: DB, LLM, payments, storage, …)
```

## Слои

| Слой | Путь | Роль |
|---|---|---|
| **Domain** | `app/domain/` | Сущности, value objects, исключения, интерфейсы репозиториев |
| **Application** | `app/application/` | Use cases, DTO, порты (LLM, payments, …), Unit of Work |
| **Infrastructure** | `app/infrastructure/` | SQLAlchemy, MinIO, YooKassa, OpenAI-совместимый LLM, worker |
| **Presentation** | `app/presentation/` | FastAPI-роутеры, схемы, deps, admin, middleware |

## Типичный поток

1. HTTP-запрос попадает в router (`presentation/routers`).
2. Dependency injection собирает use case и порты (`presentation/deps`).
3. Use case выполняет бизнес-сценарий через UoW и порты (`application/use_cases`).
4. Domain-сущности и правила живут в `domain/`.
5. Persistence и внешние сервисы — реализации в `infrastructure/`.

## HTTP API (Swagger)

Интерактивная OpenAPI-документация эндпоинтов доступна у запущенного API (маршруты в `app/presentation/routers/docs.py`), отдельно от этого MkDocs-сайта.

## API Reference

Страницы в разделе **API Reference** генерируются автоматически из дерева `app/**/*.py` при каждой сборке MkDocs. Новые модули попадают в навигацию без ручного обновления `nav`.
