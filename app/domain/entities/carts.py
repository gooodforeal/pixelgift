from dataclasses import dataclass, field
from datetime import datetime, timezone as dt_timezone
import uuid

from app.domain.entities.base import BaseEntity
from app.domain.exceptions.commerce import (
    CartItemNotFoundError,
    InvalidCartQuantityError,
)


@dataclass(frozen=False, kw_only=True)
class CartItem(BaseEntity):
    cart_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int


@dataclass(frozen=False, kw_only=True)
class Cart(BaseEntity):
    user_id: uuid.UUID
    items: list[CartItem] = field(default_factory=list)

    def add_item(self, *, product_id: uuid.UUID, quantity: int) -> CartItem:
        if quantity < 1:
            raise InvalidCartQuantityError(quantity)
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                self._touch()
                return item
        item = CartItem(cart_id=self.id, product_id=product_id, quantity=quantity)
        self.items.append(item)
        self._touch()
        return item

    def set_quantity(self, *, product_id: uuid.UUID, quantity: int) -> CartItem:
        if quantity < 1:
            raise InvalidCartQuantityError(quantity)
        for item in self.items:
            if item.product_id == product_id:
                item.quantity = quantity
                self._touch()
                return item
        raise CartItemNotFoundError(product_id)

    def remove_item(self, *, product_id: uuid.UUID) -> None:
        for index, item in enumerate(self.items):
            if item.product_id == product_id:
                del self.items[index]
                self._touch()
                return
        raise CartItemNotFoundError(product_id)

    def clear(self) -> None:
        self.items.clear()
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(dt_timezone.utc)
