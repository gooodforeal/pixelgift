import uuid

from app.domain.exceptions.base import BaseException


class ProductNotFoundError(BaseException):
    status_code = 404

    def __init__(self, *, product_id: uuid.UUID | None = None, sku: str | None = None) -> None:
        self.product_id = product_id
        self.sku = sku
        if sku is not None:
            super().__init__(f"Product not found: sku={sku!r}")
        else:
            super().__init__(f"Product not found: {product_id}")


class ProductNotAvailableError(BaseException):
    status_code = 409

    def __init__(self, sku: str) -> None:
        self.sku = sku
        super().__init__(f"Product is not available: {sku!r}")


class ProductAlreadyExistsError(BaseException):
    status_code = 409

    def __init__(self, sku: str) -> None:
        self.sku = sku
        super().__init__(f"Product already exists: sku={sku!r}")


class ProductValidationError(BaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class EmptyCartError(BaseException):
    status_code = 409

    def __init__(self) -> None:
        super().__init__("Cart is empty")


class CartItemNotFoundError(BaseException):
    status_code = 404

    def __init__(self, product_id: uuid.UUID) -> None:
        self.product_id = product_id
        super().__init__(f"Cart item not found for product: {product_id}")


class InvalidCartQuantityError(BaseException):
    def __init__(self, quantity: int) -> None:
        self.quantity = quantity
        super().__init__(f"Cart quantity must be >= 1, got {quantity}")


class OrderNotFoundError(BaseException):
    status_code = 404

    def __init__(self, order_id: uuid.UUID) -> None:
        self.order_id = order_id
        super().__init__(f"Order not found: {order_id}")


class OrderAccessDeniedError(BaseException):
    status_code = 403

    def __init__(self, order_id: uuid.UUID, actor_id: uuid.UUID) -> None:
        self.order_id = order_id
        self.actor_id = actor_id
        super().__init__(f"Actor {actor_id} cannot access order {order_id}")


class OrderNotPayableError(BaseException):
    status_code = 409

    def __init__(self, order_id: uuid.UUID, status: str) -> None:
        self.order_id = order_id
        self.status = status
        super().__init__(f"Order {order_id} with status {status!r} cannot be paid")


class InsufficientBalanceError(BaseException):
    status_code = 402

    def __init__(self, *, sku: str, required: int, available: int) -> None:
        self.sku = sku
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient balance for {sku!r}: need {required}, have {available}"
        )


class PaymentProviderError(BaseException):
    status_code = 502

    def __init__(self, message: str = "Payment provider error") -> None:
        super().__init__(message)


class PromoCodeNotFoundError(BaseException):
    status_code = 404

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Promo code not found: {code!r}")


class PromoCodeAlreadyExistsError(BaseException):
    status_code = 409

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Promo code already exists: {code!r}")


class PromoCodeFormatError(BaseException):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(
            "Promo code must be 4–20 uppercase Latin letters or digits"
        )


class PromoCodeInvalidDiscountError(BaseException):
    def __init__(self, value: int) -> None:
        self.value = value
        super().__init__(
            "Discount must be a multiple of 5 between 5 and 100"
        )


class PromoCodeExpiredError(BaseException):
    status_code = 409

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Promo code expired: {code!r}")


class PromoCodeInactiveError(BaseException):
    status_code = 409

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Promo code is inactive: {code!r}")


BOX_CREDIT_SKU = "box_credit"
