from app.domain.entities.notification_jobs import (
    NotificationJob,
    NotificationJobStatus,
    NotificationTemplate,
)
from app.infrastructure.models.notification_jobs import NotificationJobModel


def notification_job_to_model(entity: NotificationJob) -> NotificationJobModel:
    return NotificationJobModel(
        id=entity.id,
        box_id=entity.box_id,
        template=entity.template.value,
        scheduled_at=entity.scheduled_at,
        next_run_at=entity.next_run_at,
        status=entity.status.value,
        sent_at=entity.sent_at,
        last_error=entity.last_error,
        attempt_count=entity.attempt_count,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def notification_job_to_entity(model: NotificationJobModel) -> NotificationJob:
    return NotificationJob(
        id=model.id,
        box_id=model.box_id,
        template=NotificationTemplate(model.template),
        scheduled_at=model.scheduled_at,
        next_run_at=model.next_run_at,
        status=NotificationJobStatus(model.status),
        sent_at=model.sent_at,
        last_error=model.last_error,
        attempt_count=model.attempt_count,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def apply_notification_job(entity: NotificationJob, model: NotificationJobModel) -> None:
    model.box_id = entity.box_id
    model.template = entity.template.value
    model.scheduled_at = entity.scheduled_at
    model.next_run_at = entity.next_run_at
    model.status = entity.status.value
    model.sent_at = entity.sent_at
    model.last_error = entity.last_error
    model.attempt_count = entity.attempt_count
    model.updated_at = entity.updated_at
