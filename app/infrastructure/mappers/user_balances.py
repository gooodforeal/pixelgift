from app.domain.entities.user_balances import UserBalance
from app.infrastructure.models.user_balances import UserBalanceModel


def user_balance_to_model(entity: UserBalance) -> UserBalanceModel:
    return UserBalanceModel(
        id=entity.id,
        user_id=entity.user_id,
        product_id=entity.product_id,
        balance=entity.balance,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def user_balance_to_entity(model: UserBalanceModel) -> UserBalance:
    return UserBalance(
        id=model.id,
        user_id=model.user_id,
        product_id=model.product_id,
        balance=model.balance,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def apply_user_balance(entity: UserBalance, model: UserBalanceModel) -> None:
    model.user_id = entity.user_id
    model.product_id = entity.product_id
    model.balance = entity.balance
    model.updated_at = entity.updated_at
