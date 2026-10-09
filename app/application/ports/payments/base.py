"""Порт платёжного провайдера (адаптер YooKassa и аналоги)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class CreatedPayment:
    """Результат создания платежа у провайдера."""

    provider_payment_id: str
    confirmation_url: str
    status: str


@dataclass(frozen=True, kw_only=True)
class PaymentInfo:
    """Снимок состояния платежа у провайдера."""

    provider_payment_id: str
    status: str
    paid: bool
    amount_value: str
    currency: str
    metadata: dict[str, str]


class BasePaymentProvider(ABC):
    """Контракт адаптера внешней платёжной системы.

    Use case'ы создают платёж при checkout и опрашивают статус по webhook
    или при синхронизации «зависших» заказов.
    """

    @abstractmethod
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
        """Создаёт платёж и возвращает URL подтверждения для редиректа пользователя.

        Args:
            amount_kopecks: Сумма в минимальных единицах валюты (копейки для RUB).
            currency: Код валюты (ISO 4217).
            description: Описание для чека и провайдера.
            return_url: URL возврата после оплаты.
            idempotency_key: Ключ идемпотентности (обычно id заказа).
            metadata: Произвольные строковые метаданные (order_id, user_id).

        Returns:
            Идентификатор платежа у провайдера, ссылка подтверждения и статус.
        """

    @abstractmethod
    async def get_payment(self, provider_payment_id: str) -> PaymentInfo:
        """Запрашивает актуальный статус платежа по id провайдера."""
