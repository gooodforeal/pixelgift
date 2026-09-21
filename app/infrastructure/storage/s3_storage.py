from collections.abc import AsyncIterator
from datetime import timedelta

import aioboto3
from botocore.exceptions import ClientError

from app.application.ports.storage.base import BaseObjectStorage


class S3ObjectStorage(BaseObjectStorage):
    def __init__(
        self,
        *,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        region: str = "us-east-1",
    ) -> None:
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket = bucket
        self._region = region
        self._session = aioboto3.Session()

    def _client(self):
        return self._session.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            region_name=self._region,
        )

    async def upload(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str,
    ) -> None:
        async with self._client() as client:
            await client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )

    async def download(self, key: str) -> bytes:
        async with self._client() as client:
            response = await client.get_object(Bucket=self._bucket, Key=key)
            async with response["Body"] as body:
                return await body.read()

    async def delete(self, key: str) -> None:
        async with self._client() as client:
            try:
                await client.delete_object(Bucket=self._bucket, Key=key)
            except ClientError as exc:
                if exc.response["Error"]["Code"] not in {
                    "404",
                    "NoSuchKey",
                    "NotFound",
                }:
                    raise

    async def exists(self, key: str) -> bool:
        async with self._client() as client:
            try:
                await client.head_object(Bucket=self._bucket, Key=key)
            except ClientError as exc:
                if exc.response["Error"]["Code"] in {"404", "NoSuchKey", "NotFound"}:
                    return False
                raise
            return True

    async def generate_presigned_url(
        self,
        key: str,
        *,
        expires_in: timedelta = timedelta(hours=1),
    ) -> str:
        async with self._client() as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=int(expires_in.total_seconds()),
            )

    async def stream_download(self, key: str) -> AsyncIterator[bytes]:
        async with self._client() as client:
            response = await client.get_object(Bucket=self._bucket, Key=key)
            async with response["Body"] as body:
                while True:
                    chunk = await body.read(64 * 1024)
                    if not chunk:
                        break
                    yield chunk
