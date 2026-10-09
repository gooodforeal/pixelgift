"""Описания типов карточек содержимого бокса для подсказок ассистента."""

from dataclasses import dataclass

from app.domain.entities.box_items import (
    QUESTION_OPTION_MAX,
    QUESTION_OPTIONS_MAX,
    QUESTION_OPTIONS_MIN,
    QUESTION_TEXT_MAX,
    QUESTION_TEXT_MIN,
    TOY_CODES,
    BoxItemType,
)


@dataclass(frozen=True, slots=True)
class CardTypeInfo:
    """Человекочитаемое имя и правила заполнения типа карточки."""

    title: str
    description: str


CARD_TYPES: dict[str, CardTypeInfo] = {
    BoxItemType.IMAGE.value: CardTypeInfo(
        title="Фото",
        description=(
            "Карточка с загруженным изображением (JPEG, PNG, WebP). "
            "Нужен media_file_id. Опциональный caption до 300 символов. "
            "Может быть «секретным» фото (scratch-reveal) через metadata. "
            "Уместна для снимков, портретов, памятных моментов."
        ),
    ),
    BoxItemType.DRAWING.value: CardTypeInfo(
        title="Рисунок",
        description=(
            "Рисунок с встроенного холста, сохраняется как PNG-изображение. "
            "Нужен media_file_id (результат холста). Без отдельного файла с диска — "
            "пользователь рисует в UI. Хорошо для личного рукописного послания."
        ),
    ),
    BoxItemType.GIF.value: CardTypeInfo(
        title="GIF",
        description=(
            "Анимированный GIF. Нужен media_file_id с MIME image/gif. "
            "Опциональный caption. Подходит для эмоций, мемов, лёгкого настроения."
        ),
    ),
    BoxItemType.VIDEO.value: CardTypeInfo(
        title="Видео",
        description=(
            "Обычное видео (MP4, WebM, MOV). Нужен media_file_id. "
            "Опциональный caption. Для полноценных роликов, поздравлений, историй."
        ),
    ),
    BoxItemType.CIRCLE.value: CardTypeInfo(
        title="Кружок",
        description=(
            "Круглое короткое видео в стиле Telegram Circles (запись с камеры, "
            "обычно до ~60 секунд). Нужен media_file_id с видео. "
            "Живое личное обращение лицом в камеру."
        ),
    ),
    BoxItemType.VOICE.value: CardTypeInfo(
        title="Аудио",
        description=(
            "Голосовое или аудиосообщение (MP3, OGG, M4A, WAV, WebM). "
            "Нужен media_file_id. Опциональный caption. "
            "Для голосовых поздравлений и тёплых слов голосом."
        ),
    ),
    BoxItemType.TEXT.value: CardTypeInfo(
        title="Текст",
        description=(
            "Текстовая карточка без медиафайла. Обязателен непустой caption "
            "(до 300 символов) — это и есть текст. media_file_id быть не должно. "
            "Для коротких записок, стихов, признаний."
        ),
    ),
    BoxItemType.TOY.value: CardTypeInfo(
        title="Игрушка",
        description=(
            "Плюшевая игрушка из каталога без медиафайла. "
            f"В metadata обязателен toy_code из: {', '.join(sorted(TOY_CODES))}. "
            "Опциональный caption. Милый визуальный «подарок» внутри бокса."
        ),
    ),
    BoxItemType.GEOPOINT.value: CardTypeInfo(
        title="Геоточка",
        description=(
            "Точка на карте без медиафайла. В metadata обязательны числовые "
            "lat (−90…90) и lng (−180…180). Опциональный caption. "
            "Для важного места: где познакомились, куда поехать, точка свидания."
        ),
    ),
    BoxItemType.QUESTION.value: CardTypeInfo(
        title="Вопрос",
        description=(
            "Мини-викторина без медиафайла. В metadata: question "
            f"({QUESTION_TEXT_MIN}–{QUESTION_TEXT_MAX} символов), options "
            f"(список из {QUESTION_OPTIONS_MIN}–{QUESTION_OPTIONS_MAX} строк, "
            f"каждая до {QUESTION_OPTION_MAX} символов), correct_index "
            "(индекс правильного ответа, с 0). "
            "Вовлекает получателя в игру перед остальным содержимым."
        ),
    ),
}
