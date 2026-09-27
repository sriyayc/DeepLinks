from fastapi import APIRouter, Depends, Form, HTTPException, Query
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


@router.post("/shipping-address")
def change_shipping_address(
    shipping_address: str = Form(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """Intentionally CSRF-vulnerable workshop endpoint.

    A cross-origin HTML form can submit this request because it accepts ordinary
    form data and performs no CSRF-token validation. The participant's session
    cookie supplies authentication.
    """
    address = shipping_address.strip()
    if len(address) < 3 or len(address) > 255:
        raise HTTPException(status_code=400, detail="Shipping address must be 3–255 characters")

    orders = db.query(Order).filter(Order.participant_id == user.id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")

    for order in orders:
        order.shipping_address = address
    db.commit()
    return {
        "message": "Shipping address updated",
        "shipping_address": address,
        "updated_orders": len(orders),
    }


@router.get("/{order_id}")
def get_order(
    order_id: int,
    strict_authz: bool = Query(
        default=False,
        description="Enable the ownership check for the workshop comparison.",
    ),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    # INTENTIONAL IDOR: ownership is not checked unless strict mode is requested.
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if strict_authz and order.participant_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")

    items = (
        db.query(OrderItem, Product)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    return {
        "id": order.id,
        "participant_id": order.participant_id,
        "status": order.status,
        "total": order.total,
        "shipping_address": order.shipping_address,
        "items": [
            {"product_id": p.id, "name": p.name, "quantity": item.quantity}
            for item, p in items
        ],
    }
