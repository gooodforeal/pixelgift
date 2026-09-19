from abc import ABC, abstractmethod
import uuid

from src.domain.entities.support_tickets import SupportTicket, SupportTicketStatus


class BaseSupportTicketsRepository(ABC):
    @abstractmethod
    async def add(self, entity: SupportTicket) -> None: ...

    @abstractmethod
    async def get_by_id(self, id_: uuid.UUID) -> SupportTicket | None: ...

    @abstractmethod
    async def update(self, entity: SupportTicket) -> SupportTicket: ...

    @abstractmethod
    async def list_all(
        self,
        *,
        status: SupportTicketStatus | None = None,
        sort_asc: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[SupportTicket]: ...

    @abstractmethod
    async def count_all(
        self,
        *,
        status: SupportTicketStatus | None = None,
    ) -> int: ...
