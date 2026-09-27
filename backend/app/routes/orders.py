from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Order, OrderItem, Product
from ..auth import get_current_user

router = APIRouter(prefix="/api/orders", tags=["orders"])


class CheckoutItem(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=99)


class CheckoutRequest(BaseModel):
    items: list[CheckoutItem] = Field(min_length=1, max_length=50)
    shipping_address: str = Field(min_length=3, max_length=255)


@router.get("")
def list_my_orders(
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    orders = db.query(Order).filter(Order.participant_id == user.id).all()
    return [
        {
            "id": o.id,
            "status": o.status,
            "total": o.total,
            "shipping_address": o.shipping_address,
        }
        for o in orders
    ]


@router.post("/checkout", status_code=201)
def checkout(
    checkout_request: CheckoutRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    quantities: dict[int, int] = {}
    for item in checkout_request.items:
        quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity

    if any(quantity > 99 for quantity in quantities.values()):
        raise HTTPException(status_code=400, detail="Maximum quantity is 99 per product")

    products = db.query(Product).filter(Product.id.in_(quantities.keys())).all()
    products_by_id = {product.id: product for product in products}
    missing_ids = sorted(set(quantities) - set(products_by_id))
    if missing_ids:
        raise HTTPException(status_code=400, detail=f"Unknown product IDs: {missing_ids}")

    total = round(
        sum(products_by_id[product_id].price * quantity for product_id, quantity in quantities.items()),
        2,
    )
    next_order_id = (db.query(func.max(Order.id)).scalar() or 0) + 1
    order = Order(
        id=next_order_id,
        participant_id=user.id,
        status="Processing",
        total=total,
        shipping_address=checkout_request.shipping_address.strip(),
    )
    db.add(order)
    db.add_all([
        OrderItem(order_id=next_order_id, product_id=product_id, quantity=quantity)
        for product_id, quantity in quantities.items()
    ])
    db.commit()

    return {
        "id": order.id,
        "status": order.status,
        "total": order.total,
        "shipping_address": order.shipping_address,
    }


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.participant_id == user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = (
        db.query(OrderItem, Product)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    return {
        "id": order.id,
        "status": order.status,
        "total": order.total,
        "shipping_address": order.shipping_address,
        "items": [
            {"product_id": p.id, "name": p.name, "quantity": item.quantity}
            for item, p in items
        ],
    }
