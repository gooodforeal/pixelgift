"""Разбор и валидация metadata для элементов бокса (геоточка, вопрос)."""

from typing import Any

from app.domain.entities.box_items import (
    QUESTION_OPTION_MAX,
    QUESTION_OPTIONS_MAX,
    QUESTION_OPTIONS_MIN,
    QUESTION_TEXT_MAX,
    QUESTION_TEXT_MIN,
)


def parse_geopoint_metadata(metadata: dict[str, Any] | None) -> tuple[float, float]:
    """Извлекает широту и долготу из metadata и проверяет допустимые диапазоны."""
    data = metadata or {}
    lat = data.get("lat")
    lng = data.get("lng")
    if not isinstance(lat, (int, float)) or isinstance(lat, bool):
        raise ValueError("Geopoint item requires numeric metadata.lat")
    if not isinstance(lng, (int, float)) or isinstance(lng, bool):
        raise ValueError("Geopoint item requires numeric metadata.lng")
    lat_f = float(lat)
    lng_f = float(lng)
    if not (-90.0 <= lat_f <= 90.0):
        raise ValueError("metadata.lat must be between -90 and 90")
    if not (-180.0 <= lng_f <= 180.0):
        raise ValueError("metadata.lng must be between -180 and 180")
    return lat_f, lng_f


def parse_question_metadata(
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    """Проверяет и нормализует payload карточки-вопроса в metadata элемента."""
    data = metadata or {}
    raw_question = data.get("question")
    if not isinstance(raw_question, str):
        raise ValueError("Question item requires metadata.question")
    question = raw_question.strip()
    if len(question) < QUESTION_TEXT_MIN:
        raise ValueError(
            f"Question must be at least {QUESTION_TEXT_MIN} characters"
        )
    if len(question) > QUESTION_TEXT_MAX:
        raise ValueError(
            f"Question must be at most {QUESTION_TEXT_MAX} characters"
        )

    raw_options = data.get("options")
    if not isinstance(raw_options, list):
        raise ValueError("Question item requires metadata.options list")
    if not QUESTION_OPTIONS_MIN <= len(raw_options) <= QUESTION_OPTIONS_MAX:
        raise ValueError(
            f"Question must have from {QUESTION_OPTIONS_MIN} to "
            f"{QUESTION_OPTIONS_MAX} options"
        )

    options: list[str] = []
    for index, option in enumerate(raw_options):
        if not isinstance(option, str):
            raise ValueError(f"Option {index + 1} must be a string")
        text = option.strip()
        if not text:
            raise ValueError(f"Option {index + 1} must not be empty")
        if len(text) > QUESTION_OPTION_MAX:
            raise ValueError(
                f"Option {index + 1} must be at most {QUESTION_OPTION_MAX} characters"
            )
        options.append(text)

    correct = data.get("correct_index")
    if isinstance(correct, bool) or not isinstance(correct, int):
        raise ValueError("Question item requires integer metadata.correct_index")
    if not 0 <= correct < len(options):
        raise ValueError("correct_index must point to an existing option")

    return {
        "question": question,
        "options": options,
        "correct_index": correct,
    }
