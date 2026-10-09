"""Маппинг UserBalanceLog ↔ UserBalanceLogModel."""

from app.domain.entities.user_balance_logs import BalanceLogReason, UserBalanceLog
from app.infrastructure.models.user_balance_logs import UserBalanceLogModel


def user_balance_log_to_model(entity: UserBalanceLog) -> UserBalanceLogModel:
    return UserBalanceLogModel(
        id=entity.id,
        user_id=entity.user_id,
        product_id=entity.product_id,
        delta=entity.delta,
        balance_after=entity.balance_after,
        reason=entity.reason.value,
        reference_type=entity.reference_type,
        reference_id=entity.reference_id,
        created_at=entity.created_at,
    )


def user_balance_log_to_entity(model: UserBalanceLogModel) -> UserBalanceLog:
    return UserBalanceLog(
        id=model.id,
        user_id=model.user_id,
        product_id=model.product_id,
        delta=model.delta,
        balance_after=model.balance_after,
        reason=BalanceLogReason(model.reason),
        reference_type=model.reference_type,
        reference_id=model.reference_id,
        created_at=model.created_at,
        updated_at=model.created_at,
    )
