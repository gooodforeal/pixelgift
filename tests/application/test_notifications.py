from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import uuid

from app.application.ports.notifications.base import (
    BaseEmailSender,
    BaseTelegramNotifier,
)
from app.application.ports.queues.base import BaseTaskQueue
from app.application.services.notifications import (
    NotificationService,
    OwnerTelegramEvent,
    render_gift_ready_html,
    render_owner_telegram_html,
)
from app.application.use_cases.notifications import (
    DispatchDueNotificationsUseCase,
    schedule_owner_notification_job,
)
from app.application.use_cases.queries import GetPublicBoxUseCase
from app.domain.aggregates.boxes import Box, BoxStatus
from app.domain.entities.notification_jobs import (
    NotificationJob,
    NotificationJobStatus,
    NotificationTemplate,
)
from app.domain.entities.users import User
from app.domain.values.activates_at import ActivatesAt
from app.domain.values.box_recipient_email import BoxRecipientEmail
from app.domain.values.box_recipient_name import BoxRecipientName
from app.domain.values.box_title import BoxTitle
from app.domain.values.public_slug import PublicSlug
from app.domain.values.telegram_id import TelegramId
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

    async def send_photo(
        self,
        *,
        telegram_id: int,
        photo: bytes,
        filename: str,
        caption: str,
    ) -> None:
        self.messages.append(
            {
                "telegram_id": telegram_id,
                "text": caption,
                "caption": caption,
                "filename": filename,
                "photo_size": len(photo),
            }
        )


@dataclass
class RecordingTaskQueue(BaseTaskQueue):
    kicks: int = 0

    async def kick_notification_dispatch(self) -> None:
        self.kicks += 1


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
            NotificationJob.create(
                box_id=box.id,
                template=NotificationTemplate.GIFT_READY,
                scheduled_at=box.activates_at.value,
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
        assert telegram.messages[0]["filename"] == "tg-sent.png"
        assert int(telegram.messages[0]["photo_size"]) > 0
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
        job = NotificationJob.create(
            box_id=box.id,
            template=NotificationTemplate.GIFT_READY,
            scheduled_at=box.activates_at.value,
        )
        job.mark_sent()
        await uow.notification_jobs.add(job)

        email = RecordingEmailSender()
        telegram = RecordingTelegramNotifier()
        sent = await DispatchDueNotificationsUseCase(uow, _service(email, telegram)).execute()

        assert sent == 0
        assert email.messages == []
        assert telegram.messages == []

    async def test_retries_then_fails_permanently(self):
        uow = InMemoryUnitOfWork()
        owner = _owner(uuid.uuid4())
        box = _box(owner_id=owner.id)
        await uow.users.add(owner)
        await uow.boxes.add(box)
        await uow.notification_jobs.add(
            NotificationJob.create(
                box_id=box.id,
                template=NotificationTemplate.GIFT_READY,
                scheduled_at=box.activates_at.value,
            )
        )

        class BoomEmail(BaseEmailSender):
            async def send_html(self, *, to: str, subject: str, html: str) -> None:
                raise RuntimeError("smtp down")

        telegram = RecordingTelegramNotifier()
        now = datetime.now(timezone.utc)
        uc = DispatchDueNotificationsUseCase(
            uow,
            NotificationService(
                BoomEmail(),
                telegram,
                public_web_url="https://pixelgift.test",
            ),
            max_attempts=2,
        )

        first = await uc.execute(now=now)
        job = await uow.notification_jobs.get_by_box_and_template(
            box.id, NotificationTemplate.GIFT_READY
        )
        assert first == 0
        assert job is not None
        assert job.status == NotificationJobStatus.SCHEDULED
        assert job.attempt_count == 1
        assert job.last_error == "smtp down"
        assert job.scheduled_at == box.activates_at.value
        assert job.next_run_at == now + timedelta(minutes=1)

        second = await uc.execute(now=job.next_run_at)
        job = await uow.notification_jobs.get_by_box_and_template(
            box.id, NotificationTemplate.GIFT_READY
        )
        assert second == 0
        assert job is not None
        assert job.status == NotificationJobStatus.FAILED
        assert job.attempt_count == 2
        assert job.last_error == "smtp down"
        assert job.scheduled_at == box.activates_at.value

    async def test_permanent_error_does_not_retry(self):
        uow = InMemoryUnitOfWork()
        box = _box(owner_id=uuid.uuid4())
        await uow.boxes.add(box)
        await uow.notification_jobs.add(
            NotificationJob.create(
                box_id=box.id,
                template=NotificationTemplate.GIFT_READY,
                scheduled_at=box.activates_at.value,
            )
        )

        email = RecordingEmailSender()
        telegram = RecordingTelegramNotifier()
        sent = await DispatchDueNotificationsUseCase(
            uow, _service(email, telegram), max_attempts=2
        ).execute()

        job = await uow.notification_jobs.get_by_box_and_template(
            box.id, NotificationTemplate.GIFT_READY
        )
        assert sent == 0
        assert job is not None
        assert job.status == NotificationJobStatus.FAILED
        assert job.attempt_count == 0
        assert "owner not found" in (job.last_error or "").lower()
        assert email.messages == []


class TestGetPublicBoxUseCaseOpenedNotification:
    async def test_schedules_job_and_kicks_on_first_open(self):
        uow = InMemoryUnitOfWork()
        box = _box(owner_id=uuid.uuid4(), status=BoxStatus.SCHEDULED)
        await uow.boxes.add(box)
        queue = RecordingTaskQueue()

        view = await GetPublicBoxUseCase(uow, task_queue=queue).execute(
            public_slug=box.public_slug.value
        )

        assert view.content_unlocked is True
        assert view.box.first_opened_at is not None
        assert view.box.status == BoxStatus.OPENED
        assert queue.kicks == 1
        job = await uow.notification_jobs.get_by_box_and_template(
            box.id, NotificationTemplate.BOX_OPENED
        )
        assert job is not None
        assert job.status == NotificationJobStatus.SCHEDULED

    async def test_password_keeps_content_locked_until_unlock(self):
        from app.application.services.jwt import JwtService
        from app.domain.values.box_unlock_password import BoxUnlockPassword
        from app.settings import Settings

        uow = InMemoryUnitOfWork()
        box = _box(owner_id=uuid.uuid4(), status=BoxStatus.SCHEDULED)
        box.unlock_password = BoxUnlockPassword("gift2026")
        await uow.boxes.add(box)
        queue = RecordingTaskQueue()
        jwt_service = JwtService(Settings())

        locked = await GetPublicBoxUseCase(
            uow, task_queue=queue, jwt_service=jwt_service
        ).execute(public_slug=box.public_slug.value)
        assert locked.content_unlocked is False
        assert queue.kicks == 0

        from app.application.use_cases.queries import UnlockPublicBoxUseCase

        unlocked = await UnlockPublicBoxUseCase(
            uow, jwt_service, task_queue=queue
        ).execute(public_slug=box.public_slug.value, password="gift2026")
        assert unlocked.content_unlocked is True
        assert unlocked.unlock_token
        assert queue.kicks == 1
        job = await uow.notification_jobs.get_by_box_and_template(
            box.id, NotificationTemplate.BOX_OPENED
        )
        assert job is not None

    async def test_does_not_kick_on_second_open(self):
        uow = InMemoryUnitOfWork()
        box = _box(owner_id=uuid.uuid4(), status=BoxStatus.OPENED)
        box.first_opened_at = datetime.now(timezone.utc)
        await uow.boxes.add(box)
        queue = RecordingTaskQueue()

        await GetPublicBoxUseCase(uow, task_queue=queue).execute(
            public_slug=box.public_slug.value
        )

        assert queue.kicks == 0


class TestGiftReadyEmailTemplate:
    def test_fills_placeholders_and_escapes_html(self):
        html = render_gift_ready_html(
            recipient_name='Маша <script>',
            title='День & ночь',
            gift_url='https://pixelgift.test/b/gift-ready',
        )

        assert "{{recipient_name}}" not in html
        assert "{{password_block}}" not in html
        assert "Маша &lt;script&gt;" in html
        assert "День &amp; ночь" in html
        assert "https://pixelgift.test/b/gift-ready" in html
        assert "Открыть подарок" in html
        assert "from-glow-pink" not in html

    def test_includes_unlock_password(self):
        html = render_gift_ready_html(
            recipient_name="Маша",
            title="Подарок",
            gift_url="https://pixelgift.test/b/gift-ready",
            unlock_password="gift2026",
        )

        assert "gift2026" in html
        assert "Пароль для открытия" in html
        assert "{{password_block}}" not in html


class TestOwnerTelegramCaptions:
    def test_published_escapes_html_and_includes_link(self):
        owner_id = uuid.uuid4()
        box = _box(owner_id=owner_id)
        html = render_owner_telegram_html(
            OwnerTelegramEvent.PUBLISHED,
            box=box,
            public_web_url="https://pixelgift.test",
        )
        assert "🎁 <b>Pixelgift</b>" in html
        assert "Бокс опубликован" in html
        assert 'href="https://pixelgift.test/b/gift-ready"' in html
        assert ">https://pixelgift.test/b/gift-ready</a>" in html
        assert "Открыть ссылку" not in html
        assert "masha@example.com" in html
        assert "✨" not in html
        assert "📦" not in html

    def test_gift_ready_and_opened_include_visible_url(self):
        owner_id = uuid.uuid4()
        box = _box(owner_id=owner_id, status=BoxStatus.OPENED)
        box.first_opened_at = datetime(2026, 9, 14, 12, 30, tzinfo=timezone.utc)

        ready = render_owner_telegram_html(
            OwnerTelegramEvent.GIFT_READY,
            box=box,
            public_web_url="https://pixelgift.test",
        )
        opened = render_owner_telegram_html(
            OwnerTelegramEvent.OPENED,
            box=box,
            public_web_url="https://pixelgift.test",
        )

        assert ">https://pixelgift.test/b/gift-ready</a>" in ready
        assert ">https://pixelgift.test/b/gift-ready</a>" in opened
        assert ready.count("🎁") == 1
        assert opened.count("🎁") == 1
        assert "📨" not in ready
        assert "🥳" not in opened

    def test_escapes_user_content(self):
        box = _box(owner_id=uuid.uuid4())
        box.title = BoxTitle("День & ночь")
        box.recipient_name = BoxRecipientName("Маша <script>")
        html = render_owner_telegram_html(
            OwnerTelegramEvent.ARCHIVED,
            box=box,
            public_web_url="https://pixelgift.test",
        )
        assert "День &amp; ночь" in html
        assert "Маша &lt;script&gt;" in html
        assert "<script>" not in html
        assert "🎁 <b>Pixelgift</b>" in html
        assert "🗄" not in html


class TestDispatchOwnerTelegramJobs:
    async def test_dispatches_published_card(self):
        uow = InMemoryUnitOfWork()
        owner = _owner(uuid.uuid4())
        box = _box(owner_id=owner.id, status=BoxStatus.SCHEDULED)
        await uow.users.add(owner)
        await uow.boxes.add(box)
        await schedule_owner_notification_job(
            uow,
            box_id=box.id,
            template=NotificationTemplate.BOX_PUBLISHED,
        )

        email = RecordingEmailSender()
        telegram = RecordingTelegramNotifier()
        sent = await DispatchDueNotificationsUseCase(
            uow, _service(email, telegram)
        ).execute()

        assert sent == 1
        assert email.messages == []
        assert telegram.messages[0]["filename"] == "tg-published.png"
        assert "Бокс опубликован" in telegram.messages[0]["text"]

    async def test_opened_notifies_owner_once(self):
        uow = InMemoryUnitOfWork()
        owner = _owner(uuid.uuid4())
        box = _box(owner_id=owner.id, status=BoxStatus.OPENED)
        box.first_opened_at = datetime(2026, 9, 14, 12, 30, tzinfo=timezone.utc)
        await uow.users.add(owner)
        await uow.boxes.add(box)

        email = RecordingEmailSender()
        telegram = RecordingTelegramNotifier()
        uc = DispatchDueNotificationsUseCase(uow, _service(email, telegram))

        await schedule_owner_notification_job(
            uow,
            box_id=box.id,
            template=NotificationTemplate.BOX_OPENED,
            at=box.first_opened_at,
        )
        first = await uc.execute()
        second_scheduled = await schedule_owner_notification_job(
            uow,
            box_id=box.id,
            template=NotificationTemplate.BOX_OPENED,
            at=box.first_opened_at,
        )
        second = await uc.execute()

        assert first == 1
        assert second_scheduled is False
        assert second == 0
        assert len(telegram.messages) == 1
        assert "открыл" in telegram.messages[0]["text"]
        assert telegram.messages[0]["filename"] == "tg-opened.png"
        job = await uow.notification_jobs.get_by_box_and_template(
            box.id, NotificationTemplate.BOX_OPENED
        )
        assert job is not None
        assert job.status == NotificationJobStatus.SENT

