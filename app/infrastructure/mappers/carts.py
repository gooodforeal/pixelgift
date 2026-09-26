from app.domain.entities.carts import Cart, CartItem
from app.infrastructure.models.carts import CartItemModel, CartModel


def cart_item_to_model(entity: CartItem) -> CartItemModel:
    return CartItemModel(
        id=entity.id,
        cart_id=entity.cart_id,
        product_id=entity.product_id,
        quantity=entity.quantity,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def cart_item_to_entity(model: CartItemModel) -> CartItem:
    return CartItem(
        id=model.id,
        cart_id=model.cart_id,
        product_id=model.product_id,
        quantity=model.quantity,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def cart_to_model(entity: Cart) -> CartModel:
    return CartModel(
        id=entity.id,
        user_id=entity.user_id,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        items=[cart_item_to_model(item) for item in entity.items],
    )


def cart_to_entity(model: CartModel) -> Cart:
    return Cart(
        id=model.id,
        user_id=model.user_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        items=[cart_item_to_entity(item) for item in model.items],
    )


def apply_cart(entity: Cart, model: CartModel) -> None:
    model.user_id = entity.user_id
    model.updated_at = entity.updated_at

    existing = {item.id: item for item in model.items}
    keep_ids: set = set()
    for item in entity.items:
        keep_ids.add(item.id)
        if item.id in existing:
            m = existing[item.id]
            m.product_id = item.product_id
            m.quantity = item.quantity
            m.updated_at = item.updated_at
        else:
            model.items.append(cart_item_to_model(item))

    for item_id, m in list(existing.items()):
        if item_id not in keep_ids:
            model.items.remove(m)
