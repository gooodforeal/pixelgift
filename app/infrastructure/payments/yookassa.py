import logging
from decimal import Decimal, ROUND_HALF_UP

import httpx

from app.application.ports.payments.base import (
    BasePaymentProvider,
    CreatedPayment,
    PaymentInfo,
)
from app.domain.exceptions.commerce import PaymentProviderError
from app.settings import Settings

logger = logging.getLogger(__name__)

YOOKASSA_API_URL = "https://api.yookassa.ru/v3"


def _kopecks_to_amount_str(kopecks: int) -> str:
    value = (Decimal(kopecks) / Decimal(100)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return f"{value:.2f}"


class YooKassaPaymentProvider(BasePaymentProvider):
    def __init__(self, settings: Settings) -> None:
        self._shop_id = settings.yookassa_shop_id
        self._secret_key = settings.yookassa_secret_key
        self._timeout = settings.yookassa_timeout_seconds

    def _configured(self) -> bool:
        return bool(self._shop_id and self._secret_key)

    async def create_payment(
        self,
        *,
        amount_kopecks: int,
        currency: str,
        description: str,
        return_url: str,
        idempotency_key: str,
        metadata: dict[str, str],
    ) -> CreatedPayment:
        if not self._configured():
            raise PaymentProviderError("YooKassa is not configured")

        payload = {
            "amount": {
                "value": _kopecks_to_amount_str(amount_kopecks),
                "currency": currency,
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url,
            },
            "capture": True,
            "description": description[:128],
            "metadata": metadata,
        }
        data = await self._request(
            "POST",
            "/payments",
            json=payload,
            idempotency_key=idempotency_key,
        )
        confirmation = data.get("confirmation") or {}
        confirmation_url = confirmation.get("confirmation_url")
        payment_id = data.get("id")
        if not payment_id or not confirmation_url:
            raise PaymentProviderError("YooKassa create payment returned incomplete data")
        return CreatedPayment(
            provider_payment_id=str(payment_id),
            confirmation_url=str(confirmation_url),
            status=str(data.get("status") or "pending"),
        )

    async def get_payment(self, provider_payment_id: str) -> PaymentInfo:
        if not self._configured():
            raise PaymentProviderError("YooKassa is not configured")

        data = await self._request("GET", f"/payments/{provider_payment_id}")
        amount = data.get("amount") or {}
        raw_meta = data.get("metadata") or {}
        metadata = {str(k): str(v) for k, v in raw_meta.items()}
        return PaymentInfo(
            provider_payment_id=str(data.get("id") or provider_payment_id),
            status=str(data.get("status") or ""),
            paid=bool(data.get("paid")),
            amount_value=str(amount.get("value") or "0"),
            currency=str(amount.get("currency") or "RUB"),
            metadata=metadata,
        )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        idempotency_key: str | None = None,
    ) -> dict:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if idempotency_key:
            headers["Idempotence-Key"] = idempotency_key

        url = f"{YOOKASSA_API_URL}{path}"
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                auth=(self._shop_id, self._secret_key),
            ) as client:
                response = await client.request(method, url, json=json, headers=headers)
        except httpx.HTTPError as exc:
            logger.exception("YooKassa request failed: %s %s", method, path)
            raise PaymentProviderError("YooKassa request failed") from exc

        if response.status_code >= 400:
            logger.error(
                "YooKassa error %s %s: %s %s",
                method,
                path,
                response.status_code,
                response.text[:500],
            )
            raise PaymentProviderError(
                f"YooKassa error: HTTP {response.status_code}"
            )
        try:
            data = response.json()
        except ValueError as exc:
            raise PaymentProviderError("YooKassa returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise PaymentProviderError("YooKassa returned unexpected payload")
        return data
