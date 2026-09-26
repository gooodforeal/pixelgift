import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.application.dto.assistant import (
    BoxEditorFormSnapshot,
    ChatBoxAssistantCommand,
    ListBoxAssistantHistoryCommand,
)
from app.application.dto.boxes import CreateBoxCommand
from app.application.use_cases.assistant import (
    ChatBoxAssistantUseCase,
    ListBoxAssistantHistoryUseCase,
    build_box_editor_context,
)
from app.application.use_cases.boxes import CreateBoxUseCase
from app.domain.aggregates.boxes import BoxStatus
from app.domain.entities.assistant_chat_messages import (
    AssistantChatMessage,
    AssistantMessageRole,
)
from app.domain.entities.assistant_chat_threads import AssistantChatThread
from app.domain.entities.box_designs import BoxDesign
from app.domain.exceptions.assistant import (
    AssistantLlmError,
    AssistantNotConfiguredError,
    AssistantValidationError,
)
from app.domain.exceptions.boxes import BoxAccessDeniedError, BoxNotFoundError
from app.domain.values.activates_at import ActivatesAt
from app.domain.values.box_design_name import BoxDesignName
from app.domain.values.box_message import BoxMessage
from app.domain.values.box_preview_title import BoxPreviewTitle
from app.domain.values.box_recipient_email import BoxRecipientEmail
from app.domain.values.box_recipient_name import BoxRecipientName
from app.domain.values.box_title import BoxTitle
from app.domain.values.box_unlock_password import BoxUnlockPassword
from app.domain.values.url import Url
from tests.application.fakes import FakeLlmClient, InMemoryUnitOfWork


def _design() -> BoxDesign:
    return BoxDesign(
        code=f"design-{uuid.uuid4().hex[:8]}",
        name=BoxDesignName("Romantic"),
        preview_image_url=Url("https://example.com/design.png"),
        is_active=True,
    )


async def _create_box(
    uow: InMemoryUnitOfWork,
    *,
    owner_id: uuid.UUID,
    activates_at: ActivatesAt,
    assistant_thread_id: uuid.UUID | None = None,
):
    design = _design()
    await uow.box_designs.add(design)
    return await CreateBoxUseCase(uow).execute(
        CreateBoxCommand(
            owner_id=owner_id,
            design_id=design.id,
            title=BoxTitle("Happy birthday"),
            recipient_name=BoxRecipientName("Маша"),
            recipient_email=BoxRecipientEmail("masha@example.com"),
            unlock_password=BoxUnlockPassword("gift2026"),
            activates_at=activates_at,
            message=BoxMessage("For you"),
            preview_title=BoxPreviewTitle("Soon"),
            assistant_thread_id=assistant_thread_id,
        )
    )


class TestBuildBoxEditorContext:
    def test_form_only_masks_password_and_lists_missing(self) -> None:
        context = build_box_editor_context(
            step="details",
            box=None,
            form=BoxEditorFormSnapshot(
                design_id="design-1",
                title="Gift",
                recipient_name="Маша",
                recipient_email="masha@example.com",
                unlock_password_set=True,
                activates_at="2026-10-01T12:00",
            ),
        )

        assert context["box_exists"] is False
        assert context["draft_form"]["unlock_password_set"] is True
        assert "unlock_password" not in context["draft_form"]
        assert context["draft_form"]["missing_before_create"] == []

    async def test_box_context_never_includes_password_value(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ) -> None:
        uow = InMemoryUnitOfWork()
        box = await _create_box(uow, owner_id=user_id, activates_at=activates_at)

        context = build_box_editor_context(step="content", box=box, form=None)

        serialized = str(context)
        assert "gift2026" not in serialized
        assert context["box"]["unlock_password_set"] is True
        assert context["box"]["status"] == BoxStatus.DRAFT.value
        assert "items" in context["box"]["missing_for_ready_gift"]


class TestChatBoxAssistantUseCase:
    async def test_form_only_chat_persists_history(
        self,
        user_id: uuid.UUID,
    ) -> None:
        uow = InMemoryUnitOfWork()
        llm = FakeLlmClient(reply="Выберите тему на шаге Оформление.")
        uc = ChatBoxAssistantUseCase(uow, llm, max_messages=20)
        thread_id = uuid.uuid4()

        result = await uc.execute(
            ChatBoxAssistantCommand(
                user_id=user_id,
                message="С чего начать?",
                step="design",
                thread_id=thread_id,
                form=BoxEditorFormSnapshot(),
            )
        )

        assert result.reply.startswith("Выберите тему")
        assert result.thread_id == thread_id
        stored = await uow.assistant_chat_messages.list_for_thread(
            thread_id=thread_id,
            limit=20,
        )
        assert len(stored) == 2
        assert stored[0].role == AssistantMessageRole.USER
        assert stored[0].content == "С чего начать?"
        assert stored[0].thread_id == thread_id
        assert stored[1].role == AssistantMessageRole.ASSISTANT

    async def test_requires_thread_or_box(self, user_id: uuid.UUID) -> None:
        uow = InMemoryUnitOfWork()
        llm = FakeLlmClient()
        uc = ChatBoxAssistantUseCase(uow, llm)

        with pytest.raises(AssistantValidationError):
            await uc.execute(
                ChatBoxAssistantCommand(
                    user_id=user_id,
                    message="hello",
                    step="design",
                )
            )

    async def test_isolates_concurrent_threads(self, user_id: uuid.UUID) -> None:
        uow = InMemoryUnitOfWork()
        llm = FakeLlmClient(reply="ok")
        uc = ChatBoxAssistantUseCase(uow, llm, max_messages=20)
        thread_a = uuid.uuid4()
        thread_b = uuid.uuid4()

        await uc.execute(
            ChatBoxAssistantCommand(
                user_id=user_id,
                message="вопрос A",
                step="design",
                thread_id=thread_a,
            )
        )
        await uc.execute(
            ChatBoxAssistantCommand(
                user_id=user_id,
                message="вопрос B",
                step="design",
                thread_id=thread_b,
            )
        )

        messages_a = await uow.assistant_chat_messages.list_for_thread(
            thread_id=thread_a,
            limit=20,
        )
        messages_b = await uow.assistant_chat_messages.list_for_thread(
            thread_id=thread_b,
            limit=20,
        )
        assert [item.content for item in messages_a] == ["вопрос A", "ok"]
        assert [item.content for item in messages_b] == ["вопрос B", "ok"]

    async def test_loads_history_from_db_for_llm(
        self,
        user_id: uuid.UUID,
    ) -> None:
        uow = InMemoryUnitOfWork()
        thread_id = uuid.uuid4()
        await uow.assistant_chat_threads.add(
            AssistantChatThread(id=thread_id, user_id=user_id)
        )
        now = datetime.now(timezone.utc)
        await uow.assistant_chat_messages.add(
            AssistantChatMessage(
                thread_id=thread_id,
                role=AssistantMessageRole.USER,
                content="Первый вопрос",
                created_at=now - timedelta(minutes=2),
                updated_at=now - timedelta(minutes=2),
            )
        )
        await uow.assistant_chat_messages.add(
            AssistantChatMessage(
                thread_id=thread_id,
                role=AssistantMessageRole.ASSISTANT,
                content="Первый ответ",
                created_at=now - timedelta(minutes=1),
                updated_at=now - timedelta(minutes=1),
            )
        )
        llm = FakeLlmClient(reply="Второй ответ")
        uc = ChatBoxAssistantUseCase(uow, llm, max_messages=20)

        await uc.execute(
            ChatBoxAssistantCommand(
                user_id=user_id,
                message="Второй вопрос",
                step="design",
                thread_id=thread_id,
            )
        )

        sent = llm.calls[0]["messages"]
        assert isinstance(sent, list)
        assert [item.role for item in sent] == ["user", "assistant", "user"]
        assert [item.content for item in sent] == [
            "Первый вопрос",
            "Первый ответ",
            "Второй вопрос",
        ]

    async def test_trims_to_max_messages(self, user_id: uuid.UUID) -> None:
        uow = InMemoryUnitOfWork()
        llm = FakeLlmClient(reply="ok")
        uc = ChatBoxAssistantUseCase(uow, llm, max_messages=4)
        thread_id = uuid.uuid4()

        for index in range(3):
            await uc.execute(
                ChatBoxAssistantCommand(
                    user_id=user_id,
                    message=f"q{index}",
                    step="design",
                    thread_id=thread_id,
                )
            )

        visible = await uow.assistant_chat_messages.list_for_thread(
            thread_id=thread_id,
            limit=20,
        )
        assert len(visible) == 4
        assert visible[0].content == "q1"
        assert visible[-1].content == "ok"

        all_messages = list(uow.assistant_chat_messages.items.values())
        assert len(all_messages) == 6
        hidden = [item for item in all_messages if item.hidden_at is not None]
        assert len(hidden) == 2
        assert {item.content for item in hidden} == {"q0", "ok"}

    async def test_create_box_binds_thread(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ) -> None:
        uow = InMemoryUnitOfWork()
        thread_id = uuid.uuid4()
        await uow.assistant_chat_threads.add(
            AssistantChatThread(id=thread_id, user_id=user_id)
        )
        await uow.assistant_chat_messages.add(
            AssistantChatMessage(
                thread_id=thread_id,
                role=AssistantMessageRole.USER,
                content="до создания",
            )
        )
        await uow.assistant_chat_messages.add(
            AssistantChatMessage(
                thread_id=thread_id,
                role=AssistantMessageRole.ASSISTANT,
                content="ответ до создания",
            )
        )

        other_thread = uuid.uuid4()
        await uow.assistant_chat_threads.add(
            AssistantChatThread(id=other_thread, user_id=user_id)
        )
        await uow.assistant_chat_messages.add(
            AssistantChatMessage(
                thread_id=other_thread,
                role=AssistantMessageRole.USER,
                content="чужой черновик",
            )
        )

        box = await _create_box(
            uow,
            owner_id=user_id,
            activates_at=activates_at,
            assistant_thread_id=thread_id,
        )

        bound = await uow.assistant_chat_threads.get_by_id(thread_id)
        assert bound is not None
        assert bound.box_id == box.id
        other = await uow.assistant_chat_threads.get_by_id(other_thread)
        assert other is not None
        assert other.box_id is None

        llm = FakeLlmClient(reply="после создания")
        uc = ChatBoxAssistantUseCase(uow, llm, max_messages=20)
        await uc.execute(
            ChatBoxAssistantCommand(
                user_id=user_id,
                message="после",
                step="content",
                box_id=box.id,
            )
        )

        for_box = await uow.assistant_chat_messages.list_for_thread(
            thread_id=thread_id,
            limit=20,
        )
        assert [item.content for item in for_box] == [
            "до создания",
            "ответ до создания",
            "после",
            "после создания",
        ]

    async def test_loads_owned_box(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ) -> None:
        uow = InMemoryUnitOfWork()
        box = await _create_box(uow, owner_id=user_id, activates_at=activates_at)
        llm = FakeLlmClient(reply="Добавьте 2–3 карточки.")
        uc = ChatBoxAssistantUseCase(uow, llm)

        result = await uc.execute(
            ChatBoxAssistantCommand(
                user_id=user_id,
                message="Что добавить?",
                step="content",
                box_id=box.id,
            )
        )

        assert result.context["box_exists"] is True
        assert result.context["box"]["id"] == str(box.id)
        assert "gift2026" not in str(llm.calls[0]["system"])

    async def test_rejects_foreign_box(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ) -> None:
        uow = InMemoryUnitOfWork()
        box = await _create_box(uow, owner_id=user_id, activates_at=activates_at)
        llm = FakeLlmClient()
        uc = ChatBoxAssistantUseCase(uow, llm)

        with pytest.raises(BoxAccessDeniedError):
            await uc.execute(
                ChatBoxAssistantCommand(
                    user_id=uuid.uuid4(),
                    message="hello",
                    step="content",
                    box_id=box.id,
                )
            )
        assert llm.calls == []

    async def test_rejects_missing_box(self, user_id: uuid.UUID) -> None:
        uow = InMemoryUnitOfWork()
        llm = FakeLlmClient()
        uc = ChatBoxAssistantUseCase(uow, llm)

        with pytest.raises(BoxNotFoundError):
            await uc.execute(
                ChatBoxAssistantCommand(
                    user_id=user_id,
                    message="hello",
                    step="content",
                    box_id=uuid.uuid4(),
                )
            )

    async def test_not_configured(self, user_id: uuid.UUID) -> None:
        uow = InMemoryUnitOfWork()
        llm = FakeLlmClient()
        uc = ChatBoxAssistantUseCase(uow, llm, llm_configured=False)

        with pytest.raises(AssistantNotConfiguredError):
            await uc.execute(
                ChatBoxAssistantCommand(
                    user_id=user_id,
                    message="hello",
                    step="design",
                    thread_id=uuid.uuid4(),
                )
            )

    async def test_empty_message(self, user_id: uuid.UUID) -> None:
        uow = InMemoryUnitOfWork()
        llm = FakeLlmClient()
        uc = ChatBoxAssistantUseCase(uow, llm)

        with pytest.raises(AssistantValidationError):
            await uc.execute(
                ChatBoxAssistantCommand(
                    user_id=user_id,
                    message="   ",
                    step="design",
                    thread_id=uuid.uuid4(),
                )
            )

    async def test_wraps_llm_errors(self, user_id: uuid.UUID) -> None:
        uow = InMemoryUnitOfWork()
        llm = FakeLlmClient()
        llm.error = RuntimeError("boom")
        uc = ChatBoxAssistantUseCase(uow, llm)
        thread_id = uuid.uuid4()

        with pytest.raises(AssistantLlmError):
            await uc.execute(
                ChatBoxAssistantCommand(
                    user_id=user_id,
                    message="help",
                    step="design",
                    thread_id=thread_id,
                )
            )
        stored = await uow.assistant_chat_messages.count_for_thread(
            thread_id=thread_id,
        )
        assert stored == 0


class TestListBoxAssistantHistoryUseCase:
    async def test_lists_persisted_messages(self, user_id: uuid.UUID) -> None:
        uow = InMemoryUnitOfWork()
        thread_id = uuid.uuid4()
        await uow.assistant_chat_threads.add(
            AssistantChatThread(id=thread_id, user_id=user_id)
        )
        await uow.assistant_chat_messages.add(
            AssistantChatMessage(
                thread_id=thread_id,
                role=AssistantMessageRole.USER,
                content="hi",
            )
        )
        await uow.assistant_chat_messages.add(
            AssistantChatMessage(
                thread_id=thread_id,
                role=AssistantMessageRole.ASSISTANT,
                content="hello",
            )
        )
        uc = ListBoxAssistantHistoryUseCase(uow, max_messages=20)

        result = await uc.execute(
            ListBoxAssistantHistoryCommand(
                user_id=user_id,
                thread_id=thread_id,
            )
        )

        assert result.thread_id == thread_id
        assert [item.content for item in result.messages] == ["hi", "hello"]

    async def test_loads_history_by_box_after_bind(
        self,
        activates_at: ActivatesAt,
        user_id: uuid.UUID,
    ) -> None:
        uow = InMemoryUnitOfWork()
        thread_id = uuid.uuid4()
        await uow.assistant_chat_threads.add(
            AssistantChatThread(id=thread_id, user_id=user_id)
        )
        await uow.assistant_chat_messages.add(
            AssistantChatMessage(
                thread_id=thread_id,
                role=AssistantMessageRole.USER,
                content="до создания",
            )
        )
        await uow.assistant_chat_messages.add(
            AssistantChatMessage(
                thread_id=thread_id,
                role=AssistantMessageRole.ASSISTANT,
                content="ответ до создания",
            )
        )
        box = await _create_box(
            uow,
            owner_id=user_id,
            activates_at=activates_at,
            assistant_thread_id=thread_id,
        )
        uc = ListBoxAssistantHistoryUseCase(uow, max_messages=20)

        result = await uc.execute(
            ListBoxAssistantHistoryCommand(user_id=user_id, box_id=box.id)
        )

        assert result.thread_id == thread_id
        assert [item.content for item in result.messages] == [
            "до создания",
            "ответ до создания",
        ]
