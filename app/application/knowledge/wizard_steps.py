"""Справочник шагов визарда создания бокса для ассистента и UI."""

from dataclasses import dataclass
from typing import Literal

BoxWizardStepId = Literal[
    "design",
    "details",
    "content",
    "publish",
    "certificate",
]


@dataclass(frozen=True, slots=True)
class WizardStepInfo:
    """Идентификатор шага, заголовок и краткое описание для пользователя."""

    id: BoxWizardStepId
    title: str
    description: str


WIZARD_STEPS: tuple[WizardStepInfo, ...] = (
    WizardStepInfo(
        id="design",
        title="Оформление",
        description=(
            "Выбор темы бокса: фон, частицы и анимация открытия. "
            "Тема задаёт визуальный стиль подарка до и во время открытия."
        ),
    ),
    WizardStepInfo(
        id="details",
        title="Детали",
        description=(
            "Основные поля подарка: название бокса (до 30), имя получателя (до 30), "
            "email, пароль разблокировки (4–12, латиница и цифры), дата и время открытия, "
            "часовой пояс, письмо внутри (до 300), опциональный превью-заголовок. "
            "На этом шаге черновик создаётся или обновляется."
        ),
    ),
    WizardStepInfo(
        id="content",
        title="Содержимое",
        description=(
            "Наполнение бокса карточками (до 12): фото, рисунок, GIF, видео, кружок, "
            "аудио, текст, игрушка, геоточка, вопрос. Можно менять порядок и подписи. "
            "Доступен после создания черновика."
        ),
    ),
    WizardStepInfo(
        id="publish",
        title="Публикация",
        description=(
            "Проверка готовности, публичная ссылка и публикация бокса. "
            "После publish статус меняется (scheduled/active в зависимости от даты), "
            "редактирование ограничивается правилами продукта."
        ),
    ),
    WizardStepInfo(
        id="certificate",
        title="Сертификат",
        description=(
            "Скачивание PDF-сертификата с QR-кодом и паролем. "
            "Доступен после публикации — удобно распечатать или отправить отдельно от ссылки."
        ),
    ),
)
