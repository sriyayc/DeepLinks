from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Order, OrderItem, Product
from ..auth import get_current_user

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.get("")
def list_my_orders(
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    orders = db.query(Order).filter(Order.user_id == user.id).all()
    return [
        {
            "id": o.id,
            "status": o.status,
            "total": o.total,
            "shipping_address": o.shipping_address,
        }
        for o in orders
    ]

@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    # Secure baseline: ownership is checked here.
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == user.id)
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
