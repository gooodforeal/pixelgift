from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import uuid

from src.application.ports.notifications import BaseEmailSender, BaseTelegramNotifier
from src.application.ports.task_queue import BaseTaskQueue
from src.application.services.notifications import NotificationService, render_gift_ready_html
from src.application.use_cases.notifications import (
    DispatchDueNotificationsUseCase,
    NotifyBoxOpenedUseCase,
)
from src.application.use_cases.queries import GetPublicBoxUseCase
from src.domain.aggregates.boxes import Box, BoxStatus
from src.domain.entities.notification_jobs import (
    NotificationJob,
    NotificationJobStatus,
    NotificationTemplate,
)
from src.domain.entities.users import User
from src.domain.values.activates_at import ActivatesAt
from src.domain.values.box_recipient_email import BoxRecipientEmail
from src.domain.values.box_recipient_name import BoxRecipientName
from src.domain.values.box_title import BoxTitle
from src.domain.values.public_slug import PublicSlug
from src.domain.values.telegram_id import TelegramId
from tests.application.fakes import InMemoryUnitOfWork


@dataclass
class RecordingEmailSender(BaseEmailSender):
    messages: list[dict[str, str]] = field(default_factory=list)

    async def send_html(self, *, to: str, subject: str, html: str) -> None:
        self.messages.append({"to": to, "subject": subject, "html": html})


@dataclass
class RecordingTelegramNotifier(BaseTelegramNotifier):
    messages: list[dict[str, object]] = field(default_factory=list)

    async def send_message(self, *, telegram_id: int, text: str) -> None:
        self.messages.append({"telegram_id": telegram_id, "text": text})


@dataclass
class RecordingTaskQueue(BaseTaskQueue):
    opened: list[uuid.UUID] = field(default_factory=list)

    async def enqueue_box_opened(self, box_id: uuid.UUID) -> None:
        self.opened.append(box_id)


def _service(
    email: RecordingEmailSender,
    telegram: RecordingTelegramNotifier,
) -> NotificationService:
    return NotificationService(
        email,
        telegram,
        public_web_url="https://pixelgift.test",
    )


def _owner(user_id: uuid.UUID) -> User:
    return User(
        id=user_id,
        telegram_id=TelegramId("123456789"),
        first_name="Alice",
    )


def _box(*, owner_id: uuid.UUID, status: BoxStatus = BoxStatus.SCHEDULED) -> Box:
    return Box(
        owner_id=owner_id,
        design_id=uuid.uuid4(),
        public_slug=PublicSlug("gift-ready"),
        title=BoxTitle("Happy birthday"),
        recipient_name=BoxRecipientName("Маша"),
        recipient_email=BoxRecipientEmail("masha@example.com"),
        activates_at=ActivatesAt.reconstitute(
            datetime.now(timezone.utc) - timedelta(minutes=1)
        ),
        status=status,
        timezone="Europe/Moscow",
    )


class TestDispatchDueNotificationsUseCase:
    async def test_sends_email_and_telegram_to_owner(self):
        uow = InMemoryUnitOfWork()
        owner = _owner(uuid.uuid4())
        box = _box(owner_id=owner.id)
        await uow.users.add(owner)
        await uow.boxes.add(box)
        await uow.notification_jobs.add(
            NotificationJob(
                box_id=box.id,
                template=NotificationTemplate.GIFT_READY,
                run_at=box.activates_at.value,
            )
        )

        email = RecordingEmailSender()
        telegram = RecordingTelegramNotifier()
        sent = await DispatchDueNotificationsUseCase(uow, _service(email, telegram)).execute()

        assert sent == 1
        assert len(email.messages) == 1
        assert email.messages[0]["to"] == "masha@example.com"
        assert "https://pixelgift.test/b/gift-ready" in email.messages[0]["html"]
        assert "Pixelgift" in email.messages[0]["html"]
        assert "Маша" in email.messages[0]["html"]
        assert telegram.messages[0]["telegram_id"] == 123456789
        assert "отправлен" in telegram.messages[0]["text"]
        job = await uow.notification_jobs.get_by_box_and_template(
            box.id, NotificationTemplate.GIFT_READY
        )
        assert job is not None
        assert job.status == NotificationJobStatus.SENT

    async def test_does_not_resend_already_sent(self):
        uow = InMemoryUnitOfWork()
        owner = _owner(uuid.uuid4())
        box = _box(owner_id=owner.id)
        await uow.users.add(owner)
        await uow.boxes.add(box)
        job = NotificationJob(
            box_id=box.id,
            template=NotificationTemplate.GIFT_READY,
            run_at=box.activates_at.value,
        )
        job.mark_sent()
        await uow.notification_jobs.add(job)

        email = RecordingEmailSender()
        telegram = RecordingTelegramNotifier()
        sent = await DispatchDueNotificationsUseCase(uow, _service(email, telegram)).execute()

        assert sent == 0
        assert email.messages == []
        assert telegram.messages == []


class TestNotifyBoxOpenedUseCase:
    async def test_notifies_owner_once(self):
        uow = InMemoryUnitOfWork()
        owner = _owner(uuid.uuid4())
        box = _box(owner_id=owner.id, status=BoxStatus.ACTIVE)
        box.first_opened_at = datetime(2026, 9, 14, 12, 30, tzinfo=timezone.utc)
        await uow.users.add(owner)
        await uow.boxes.add(box)

        email = RecordingEmailSender()
        telegram = RecordingTelegramNotifier()
        service = _service(email, telegram)

        first = await NotifyBoxOpenedUseCase(uow, service).execute(box_id=box.id)
        second = await NotifyBoxOpenedUseCase(uow, service).execute(box_id=box.id)

        assert first is True
        assert second is False
        assert len(telegram.messages) == 1
        assert "открыл" in telegram.messages[0]["text"]
        assert "Happy birthday" in telegram.messages[0]["text"]
        assert email.messages == []


class TestGetPublicBoxUseCaseOpenedNotification:
    async def test_enqueues_on_first_open(self):
        uow = InMemoryUnitOfWork()
        box = _box(owner_id=uuid.uuid4(), status=BoxStatus.SCHEDULED)
        await uow.boxes.add(box)
        queue = RecordingTaskQueue()

        view = await GetPublicBoxUseCase(uow, task_queue=queue).execute(
            public_slug=box.public_slug.value
        )

        assert view.content_unlocked is True
        assert view.box.first_opened_at is not None
        assert view.box.status == BoxStatus.ACTIVE
        assert queue.opened == [box.id]

    async def test_does_not_enqueue_on_second_open(self):
        uow = InMemoryUnitOfWork()
        box = _box(owner_id=uuid.uuid4(), status=BoxStatus.ACTIVE)
        box.first_opened_at = datetime.now(timezone.utc)
        await uow.boxes.add(box)
        queue = RecordingTaskQueue()

        await GetPublicBoxUseCase(uow, task_queue=queue).execute(
            public_slug=box.public_slug.value
        )

        assert queue.opened == []


class TestGiftReadyEmailTemplate:
    def test_fills_placeholders_and_escapes_html(self):
        html = render_gift_ready_html(
            recipient_name='Маша <script>',
            title='День & ночь',
            gift_url='https://pixelgift.test/b/gift-ready',
        )

        assert "{{recipient_name}}" not in html
        assert "Маша &lt;script&gt;" in html
        assert "День &amp; ночь" in html
        assert "https://pixelgift.test/b/gift-ready" in html
        assert "Открыть подарок" in html
        assert "from-glow-pink" not in html
