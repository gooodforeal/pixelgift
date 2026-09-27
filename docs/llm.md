На каждый вызов complete уходит две части: system и messages.

1. system (одна строка)
SYSTEM_PROMPT + JSON-контекст редактора.

A. Фиксированный SYSTEM_PROMPT — роль Гифти, описание продукта, правила, оффтоп, стиль, шаги визарда, статусы.

B. JSON из build_box_editor_context — всегда:

current_step, current_step_title, current_step_hint
wizard_steps[] — id / title / description всех шагов
card_types[] — type / title / description всех типов карточек
limits — max_items: 12, max_title/recipient_name: 30, max_message: 300
box_exists — bool
C. Если бокс уже есть (box_id) — блок box:

id, status, design_id
title, recipient_name
recipient_email_set, unlock_password_set (только флаги, не сами значения)
activates_at, timezone
message_set, preview_title_set (флаги, не текст)
items_count, item_types[] (только типы: image, text, … — без caption/media/metadata)
items_remaining, published_at
missing_for_ready_gift[] — чего не хватает (title, items, publish, …)
D. Если бокса ещё нет — блок draft_form:

флаги/черновики полей с фронта (design_id_set, title, recipient_name, …)
missing_before_create[]
Пароль, email, текст письма, содержимое карточек в LLM не уходят.

2. messages (диалог)
История треда из БД — до max_messages - 2 (по умолчанию 18), роли user / assistant, только content
Текущее сообщение пользователя (до 2000 символов)