#!/usr/bin/env python3
from __future__ import annotations

import mimetypes
import os
import sys
import time
import uuid
from pathlib import Path

import boto3
import psycopg
from botocore.client import BaseClient
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
ASSETS_ROOT = ROOT / "assets"

# Stable namespace so re-runs keep the same design asset ids.
_SEED_NAMESPACE = uuid.UUID("6f1a1d5e-0000-4000-8000-000000000000")

# Predefined box design codes → local preview file under assets/designs/.
DESIGN_PREVIEWS: dict[str, str] = {
    "romantic": "romantic.jpg",
    "birthday": "birthday.jpg",
    "winter": "winter.jpg",
    "golden": "golden.jpg",
    "spring": "spring.jpg",
    "retro": "retro.jpg",
}


def _env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None or value == "":
        raise SystemExit(f"Missing required env var: {name}")
    return value


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _content_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def _database_url() -> str:
    return (
        _env(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/pixelgift",
        )
        .replace("postgresql+asyncpg://", "postgresql://")
        .replace("postgresql+psycopg://", "postgresql://")
    )


def _api_base_url() -> str:
    return _env("API_BASE_URL", "http://localhost:8000").rstrip("/")


def _design_asset_id(code: str) -> uuid.UUID:
    return uuid.uuid5(_SEED_NAMESPACE, f"design-preview:{code}")


def _object_matches(client: BaseClient, bucket: str, key: str, path: Path) -> bool:
    try:
        head = client.head_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise
    return int(head.get("ContentLength", -1)) == path.stat().st_size


def _ensure_bucket(client: BaseClient, bucket: str, *, attempts: int = 60) -> None:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            try:
                client.head_bucket(Bucket=bucket)
                print(f"  bucket ready: {bucket}", flush=True)
                return
            except ClientError as exc:
                code = str(exc.response.get("Error", {}).get("Code", ""))
                http_status = exc.response.get("ResponseMetadata", {}).get(
                    "HTTPStatusCode"
                )
                if code in {"403", "AccessDenied", "InvalidAccessKeyId", "SignatureDoesNotMatch"}:
                    raise
                # 404 / NoSuchBucket → create; other transient errors → retry.
                if code in {"404", "NoSuchBucket", "NotFound"} or http_status == 404:
                    try:
                        client.create_bucket(Bucket=bucket)
                        print(f"  created bucket: {bucket}", flush=True)
                        return
                    except ClientError as create_exc:
                        create_code = str(
                            create_exc.response.get("Error", {}).get("Code", "")
                        )
                        if create_code in {
                            "BucketAlreadyOwnedByYou",
                            "BucketAlreadyExists",
                        }:
                            print(f"  bucket ready: {bucket}", flush=True)
                            return
                        raise
                last_error = exc
        except ClientError as exc:
            last_error = exc
            code = str(exc.response.get("Error", {}).get("Code", ""))
            if code in {"403", "AccessDenied", "InvalidAccessKeyId", "SignatureDoesNotMatch"}:
                raise

        if attempt == attempts - 1:
            break
        time.sleep(1)

    raise SystemExit(f"MinIO bucket not ready: {bucket} ({last_error})")


def _ensure_object(
    client: BaseClient,
    *,
    bucket: str,
    key: str,
    path: Path,
) -> str:
    """Upload if missing/changed. Returns 'put' or 'skip'."""
    if _object_matches(client, bucket, key, path):
        print(f"  skip  {key}", flush=True)
        return "skip"

    client.upload_file(
        Filename=str(path),
        Bucket=bucket,
        Key=key,
        ExtraArgs={"ContentType": _content_type(path)},
    )
    print(f"  put   {key}", flush=True)
    return "put"


def _seed_designs(client: BaseClient, bucket: str) -> tuple[int, int]:
    designs_dir = ASSETS_ROOT / "designs"
    if not designs_dir.is_dir():
        raise SystemExit(f"Seed directory not found: {designs_dir}")

    api_base = _api_base_url()
    uploaded = skipped = 0

    with psycopg.connect(_database_url()) as conn:
        for code, filename in DESIGN_PREVIEWS.items():
            path = designs_dir / filename
            if not path.is_file():
                raise SystemExit(f"Missing design preview file: {path}")

            asset_id = _design_asset_id(code)
            extension = path.suffix.lower()
            storage_key = f"designs/{asset_id}{extension}"
            mime = _content_type(path)
            size_bytes = path.stat().st_size
            preview_url = f"{api_base}/designs/assets/{asset_id}"

            result = _ensure_object(
                client, bucket=bucket, key=storage_key, path=path
            )
            if result == "put":
                uploaded += 1
            else:
                skipped += 1

            conn.execute(
                """
                INSERT INTO design_assets (
                    id, storage_key, mime_type, size_bytes, original_filename, created_at
                )
                VALUES (
                    %(id)s, %(storage_key)s, %(mime_type)s, %(size_bytes)s,
                    %(original_filename)s, now()
                )
                ON CONFLICT (id) DO UPDATE SET
                    storage_key = EXCLUDED.storage_key,
                    mime_type = EXCLUDED.mime_type,
                    size_bytes = EXCLUDED.size_bytes,
                    original_filename = EXCLUDED.original_filename
                """,
                {
                    "id": asset_id,
                    "storage_key": storage_key,
                    "mime_type": mime,
                    "size_bytes": size_bytes,
                    "original_filename": filename,
                },
            )
            updated = conn.execute(
                """
                UPDATE box_designs
                SET preview_image_url = %(preview_url)s
                WHERE code = %(code)s
                """,
                {"preview_url": preview_url, "code": code},
            )
            if updated.rowcount == 0:
                print(
                    f"  warn  box_designs row missing for code={code}",
                    flush=True,
                )
            else:
                print(f"  link  {code} -> {preview_url}", flush=True)

        conn.commit()

    return uploaded, skipped


def main() -> int:
    _load_dotenv()
    endpoint = _env("MINIO_ENDPOINT", "http://localhost:9000")
    access_key = _env("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = _env("MINIO_SECRET_KEY", "minioadmin")
    bucket = _env("MINIO_BUCKET", "pixelgift")
    region = os.environ.get("MINIO_REGION", "us-east-1")

    if not ASSETS_ROOT.is_dir():
        raise SystemExit(f"Assets root not found: {ASSETS_ROOT}")

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )

    print(f"Ensuring bucket s3://{bucket} ...", flush=True)
    _ensure_bucket(client, bucket)

    print("Seeding design previews into designs/ + design_assets ...", flush=True)
    designs_put, designs_skip = _seed_designs(client, bucket)

    print(
        f"Seed complete (designs put={designs_put} skip={designs_skip})",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
