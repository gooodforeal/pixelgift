from sqladmin import ModelView
from sqladmin.filters import AllUniqueStringValuesFilter

from app.infrastructure.models.box_designs import BoxDesignModel
from app.infrastructure.models.box_items import BoxItemModel
from app.infrastructure.models.boxes import BoxModel
from app.infrastructure.models.design_assets import DesignAssetModel
from app.infrastructure.models.design_ratings import DesignRatingModel
from app.infrastructure.models.media_files import MediaFileModel
from app.infrastructure.models.notification_jobs import NotificationJobModel
from app.infrastructure.models.support_tickets import (
    SupportTicketAttachmentModel,
    SupportTicketModel,
)
from app.infrastructure.models.telegram_login_challenges import (
    TelegramLoginChallengeModel,
)
from app.infrastructure.models.user_sessions import UserSessionModel
from app.infrastructure.models.users import UserModel


class UserAdmin(ModelView, model=UserModel):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
    category = "Люди"
    column_list = [
        UserModel.id,
        UserModel.telegram_id,
        UserModel.username,
        UserModel.first_name,
        UserModel.last_name,
        UserModel.is_active,
        UserModel.is_admin,
        UserModel.notifications_enabled,
        UserModel.last_seen_at,
        UserModel.created_at,
    ]
    column_searchable_list = [
        UserModel.username,
        UserModel.first_name,
        UserModel.last_name,
        UserModel.telegram_id,
    ]
    column_sortable_list = [
        UserModel.created_at,
        UserModel.last_seen_at,
        UserModel.is_admin,
        UserModel.is_active,
    ]
    column_default_sort = [(UserModel.created_at, True)]
    form_excluded_columns = [UserModel.created_at, UserModel.updated_at]
    can_create = False


class UserSessionAdmin(ModelView, model=UserSessionModel):
    name = "Сессия"
    name_plural = "Сессии"
    icon = "fa-solid fa-key"
    category = "Люди"
    column_list = [
        UserSessionModel.id,
        UserSessionModel.user_id,
        UserSessionModel.expires_at,
        UserSessionModel.revoked_at,
        UserSessionModel.user_agent,
        UserSessionModel.created_at,
    ]
    column_details_exclude_list = [UserSessionModel.refresh_token_hash]
    form_excluded_columns = [
        UserSessionModel.refresh_token_hash,
        UserSessionModel.created_at,
    ]
    can_create = False
    column_default_sort = [(UserSessionModel.created_at, True)]


class TelegramLoginChallengeAdmin(ModelView, model=TelegramLoginChallengeModel):
    name = "Код входа"
    name_plural = "Коды входа"
    icon = "fa-brands fa-telegram"
    category = "Люди"
    column_list = [
        TelegramLoginChallengeModel.code,
        TelegramLoginChallengeModel.status,
        TelegramLoginChallengeModel.telegram_id,
        TelegramLoginChallengeModel.user_id,
        TelegramLoginChallengeModel.expires_at,
        TelegramLoginChallengeModel.completed_at,
        TelegramLoginChallengeModel.created_at,
    ]
    can_create = False
    column_default_sort = [(TelegramLoginChallengeModel.created_at, True)]


class BoxAdmin(ModelView, model=BoxModel):
    name = "Бокс"
    name_plural = "Боксы"
    icon = "fa-solid fa-gift"
    category = "Подарки"
    column_list = [
        BoxModel.id,
        BoxModel.public_slug,
        BoxModel.title,
        BoxModel.recipient_name,
        BoxModel.recipient_email,
        BoxModel.status,
        BoxModel.activates_at,
        BoxModel.owner_id,
        BoxModel.created_at,
    ]
    column_searchable_list = [
        BoxModel.public_slug,
        BoxModel.title,
        BoxModel.recipient_name,
        BoxModel.recipient_email,
    ]
    column_sortable_list = [
        BoxModel.created_at,
        BoxModel.activates_at,
        BoxModel.status,
    ]
    form_excluded_columns = [BoxModel.created_at, BoxModel.updated_at, BoxModel.items]
    column_default_sort = [(BoxModel.created_at, True)]


class BoxItemAdmin(ModelView, model=BoxItemModel):
    name = "Момент"
    name_plural = "Моменты"
    icon = "fa-solid fa-layer-group"
    category = "Подарки"
    column_list = [
        BoxItemModel.id,
        BoxItemModel.box_id,
        BoxItemModel.item_type,
        BoxItemModel.sort_order,
        BoxItemModel.caption,
        BoxItemModel.created_at,
    ]
    form_excluded_columns = [BoxItemModel.created_at, BoxItemModel.box]
    column_default_sort = [(BoxItemModel.created_at, True)]


class MediaFileAdmin(ModelView, model=MediaFileModel):
    name = "Медиафайл"
    name_plural = "Медиафайлы"
    icon = "fa-solid fa-photo-film"
    category = "Подарки"
    column_list = [
        MediaFileModel.id,
        MediaFileModel.owner_id,
        MediaFileModel.media_kind,
        MediaFileModel.mime_type,
        MediaFileModel.original_filename,
        MediaFileModel.size_bytes,
        MediaFileModel.created_at,
    ]
    form_excluded_columns = [MediaFileModel.created_at]
    column_searchable_list = [MediaFileModel.original_filename, MediaFileModel.storage_key]
    column_default_sort = [(MediaFileModel.created_at, True)]


class NotificationJobAdmin(ModelView, model=NotificationJobModel):
    name = "notification_jobs"
    name_plural = "notification_jobs"
    icon = "fa-solid fa-bell"
    category = "Очереди"
    column_list = [
        NotificationJobModel.id,
        NotificationJobModel.box_id,
        NotificationJobModel.template,
        NotificationJobModel.status,
        NotificationJobModel.scheduled_at,
        NotificationJobModel.next_run_at,
        NotificationJobModel.attempt_count,
        NotificationJobModel.last_error,
        NotificationJobModel.sent_at,
    ]
    column_searchable_list = [
        NotificationJobModel.template,
        NotificationJobModel.status,
        NotificationJobModel.last_error,
    ]
    column_filters = [
        AllUniqueStringValuesFilter(NotificationJobModel.status),
        AllUniqueStringValuesFilter(NotificationJobModel.template),
    ]
    column_sortable_list = [
        NotificationJobModel.next_run_at,
        NotificationJobModel.scheduled_at,
        NotificationJobModel.status,
        NotificationJobModel.attempt_count,
        NotificationJobModel.sent_at,
    ]
    form_excluded_columns = [
        NotificationJobModel.created_at,
        NotificationJobModel.updated_at,
    ]
    column_default_sort = [(NotificationJobModel.next_run_at, True)]


class BoxDesignAdmin(ModelView, model=BoxDesignModel):
    name = "Дизайн"
    name_plural = "Дизайны"
    icon = "fa-solid fa-palette"
    category = "Оформление"
    column_list = [
        BoxDesignModel.code,
        BoxDesignModel.name,
        BoxDesignModel.is_active,
        BoxDesignModel.sort_order,
        BoxDesignModel.created_at,
    ]
    column_searchable_list = [BoxDesignModel.code, BoxDesignModel.name]
    form_excluded_columns = [BoxDesignModel.created_at, BoxDesignModel.updated_at]
    column_default_sort = [(BoxDesignModel.sort_order, False)]


class DesignAssetAdmin(ModelView, model=DesignAssetModel):
    name = "Ассет дизайна"
    name_plural = "Ассеты дизайнов"
    icon = "fa-solid fa-image"
    category = "Оформление"
    column_list = [
        DesignAssetModel.id,
        DesignAssetModel.original_filename,
        DesignAssetModel.mime_type,
        DesignAssetModel.size_bytes,
        DesignAssetModel.created_at,
    ]
    form_excluded_columns = [DesignAssetModel.created_at]
    column_default_sort = [(DesignAssetModel.created_at, True)]


class DesignRatingAdmin(ModelView, model=DesignRatingModel):
    name = "Оценка"
    name_plural = "Оценки"
    icon = "fa-solid fa-star"
    category = "Оформление"
    column_list = [
        DesignRatingModel.id,
        DesignRatingModel.user_id,
        DesignRatingModel.design_id,
        DesignRatingModel.stars,
        DesignRatingModel.created_at,
    ]
    form_excluded_columns = [
        DesignRatingModel.created_at,
        DesignRatingModel.updated_at,
    ]
    column_default_sort = [(DesignRatingModel.created_at, True)]


class SupportTicketAdmin(ModelView, model=SupportTicketModel):
    name = "Тикет"
    name_plural = "Тикеты"
    icon = "fa-solid fa-headset"
    category = "Поддержка"
    column_list = [
        SupportTicketModel.id,
        SupportTicketModel.subject,
        SupportTicketModel.contact,
        SupportTicketModel.status,
        SupportTicketModel.created_at,
    ]
    column_searchable_list = [
        SupportTicketModel.subject,
        SupportTicketModel.contact,
        SupportTicketModel.description,
    ]
    form_excluded_columns = [
        SupportTicketModel.created_at,
        SupportTicketModel.updated_at,
        SupportTicketModel.attachments,
    ]
    column_default_sort = [(SupportTicketModel.created_at, True)]


class SupportTicketAttachmentAdmin(ModelView, model=SupportTicketAttachmentModel):
    name = "Вложение"
    name_plural = "Вложения"
    icon = "fa-solid fa-paperclip"
    category = "Поддержка"
    column_list = [
        SupportTicketAttachmentModel.id,
        SupportTicketAttachmentModel.ticket_id,
        SupportTicketAttachmentModel.original_filename,
        SupportTicketAttachmentModel.mime_type,
        SupportTicketAttachmentModel.size_bytes,
        SupportTicketAttachmentModel.created_at,
    ]
    form_excluded_columns = [
        SupportTicketAttachmentModel.created_at,
        SupportTicketAttachmentModel.ticket,
    ]
    can_create = False
    column_default_sort = [(SupportTicketAttachmentModel.created_at, True)]


ADMIN_VIEWS = [
    NotificationJobAdmin,
    UserAdmin,
    UserSessionAdmin,
    TelegramLoginChallengeAdmin,
    BoxAdmin,
    BoxItemAdmin,
    MediaFileAdmin,
    BoxDesignAdmin,
    DesignAssetAdmin,
    DesignRatingAdmin,
    SupportTicketAdmin,
    SupportTicketAttachmentAdmin,
]
