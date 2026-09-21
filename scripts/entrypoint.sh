#!/usr/bin/env sh
set -e

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os
import time

import psycopg

# psycopg accepts libpq URLs (postgresql://...), not SQLAlchemy dialects.
url = (
    os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@db:5432/pixelgift",
    )
    .replace("postgresql+asyncpg://", "postgresql://")
    .replace("postgresql+psycopg://", "postgresql://")
)

for attempt in range(60):
    try:
        with psycopg.connect(url) as conn:
            conn.execute("SELECT 1")
        print("PostgreSQL is ready")
        break
    except Exception as exc:
        if attempt == 59:
            raise SystemExit(f"PostgreSQL is not ready: {exc}") from exc
        time.sleep(1)
PY

echo "Running migrations..."
alembic upgrade head

echo "Seeding design assets into MinIO..."
python /app/scripts/seed_static_assets.py

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
