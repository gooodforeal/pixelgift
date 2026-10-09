"""ORM-модель балансов пользователей."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.infrastructure.models.products import ProductModel


class UserBalanceModel(TimestampMixin, Base):
    """Баланс единиц товара у пользователя."""

    __tablename__ = "user_balances"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_user_balances_user_product",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("products.id"),
        nullable=False,
    )
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    product: Mapped["ProductModel"] = relationship(back_populates="balances")
