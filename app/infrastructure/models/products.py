"""ORM-модель товаров."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.infrastructure.models.carts import CartItemModel
    from app.infrastructure.models.orders import OrderItemModel
    from app.infrastructure.models.product_sales import ProductSaleModel
    from app.infrastructure.models.user_balances import UserBalanceModel


class ProductModel(TimestampMixin, Base):
    """Товар витрины; цены в минорных единицах (копейки)."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    sku: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    image_urls: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="RUB")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    cart_items: Mapped[list["CartItemModel"]] = relationship(back_populates="product")
    order_items: Mapped[list["OrderItemModel"]] = relationship(back_populates="product")
    balances: Mapped[list["UserBalanceModel"]] = relationship(back_populates="product")
    sale: Mapped["ProductSaleModel | None"] = relationship(
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )
