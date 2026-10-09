"""ORM-модель тредов чата ассистента."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class AssistantChatThreadModel(Base):
    """Диалог ассистента; опционально привязан к одной коробке."""

    __tablename__ = "assistant_chat_threads"
    __table_args__ = (Index("ix_assistant_chat_threads_user_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    box_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("boxes.id", ondelete="CASCADE"),
        nullable=True,
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
