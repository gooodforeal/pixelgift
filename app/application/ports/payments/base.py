from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class CreatedPayment:
    provider_payment_id: str
    confirmation_url: str
    status: str


@dataclass(frozen=True, kw_only=True)
class PaymentInfo:
    provider_payment_id: str
    status: str
    paid: bool
    amount_value: str
    currency: str
    metadata: dict[str, str]


class BasePaymentProvider(ABC):
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
    ) -> CreatedPayment: ...

    @abstractmethod
    async def get_payment(self, provider_payment_id: str) -> PaymentInfo: ...
