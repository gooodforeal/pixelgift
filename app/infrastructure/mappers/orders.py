from app.domain.entities.orders import Order, OrderItem, OrderStatus
from app.infrastructure.models.orders import OrderItemModel, OrderModel


def order_item_to_model(entity: OrderItem) -> OrderItemModel:
    return OrderItemModel(
        id=entity.id,
        order_id=entity.order_id,
        product_id=entity.product_id,
        quantity=entity.quantity,
        unit_price=entity.unit_price,
        amount=entity.amount,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def order_item_to_entity(model: OrderItemModel) -> OrderItem:
    return OrderItem(
        id=model.id,
        order_id=model.order_id,
        product_id=model.product_id,
        quantity=model.quantity,
        unit_price=model.unit_price,
        amount=model.amount,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def order_to_model(entity: Order) -> OrderModel:
    return OrderModel(
        id=entity.id,
        user_id=entity.user_id,
        status=entity.status.value,
        amount=entity.amount,
        currency=entity.currency,
        provider=entity.provider,
        provider_payment_id=entity.provider_payment_id,
        idempotency_key=entity.idempotency_key,
        confirmation_url=entity.confirmation_url,
        paid_at=entity.paid_at,
        promo_code_id=entity.promo_code_id,
        discount_percent=entity.discount_percent,
        amount_before_discount=entity.amount_before_discount,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        items=[order_item_to_model(item) for item in entity.items],
    )


def order_to_entity(model: OrderModel) -> Order:
    return Order(
        id=model.id,
        user_id=model.user_id,
        status=OrderStatus(model.status),
        amount=model.amount,
        currency=model.currency,
        provider=model.provider,
        provider_payment_id=model.provider_payment_id,
        idempotency_key=model.idempotency_key,
        confirmation_url=model.confirmation_url,
        paid_at=model.paid_at,
        promo_code_id=model.promo_code_id,
        discount_percent=model.discount_percent,
        amount_before_discount=model.amount_before_discount,
        created_at=model.created_at,
        updated_at=model.updated_at,
        items=[order_item_to_entity(item) for item in model.items],
    )


def apply_order(entity: Order, model: OrderModel) -> None:
    model.user_id = entity.user_id
    model.status = entity.status.value
    model.amount = entity.amount
    model.currency = entity.currency
    model.provider = entity.provider
    model.provider_payment_id = entity.provider_payment_id
    model.idempotency_key = entity.idempotency_key
    model.confirmation_url = entity.confirmation_url
    model.paid_at = entity.paid_at
    model.promo_code_id = entity.promo_code_id
    model.discount_percent = entity.discount_percent
    model.amount_before_discount = entity.amount_before_discount
    model.updated_at = entity.updated_at

    existing = {item.id: item for item in model.items}
    keep_ids: set = set()
    for item in entity.items:
        keep_ids.add(item.id)
        if item.id in existing:
            m = existing[item.id]
            m.product_id = item.product_id
            m.quantity = item.quantity
            m.unit_price = item.unit_price
            m.amount = item.amount
            m.updated_at = item.updated_at
        else:
            model.items.append(order_item_to_model(item))

    for item_id, m in list(existing.items()):
        if item_id not in keep_ids:
            model.items.remove(m)
