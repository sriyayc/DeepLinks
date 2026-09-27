from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import CartItem, Order, OrderItem, Participant, Product

router = APIRouter(prefix="/api/cart", tags=["cart"])


class AddCartItem(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=99)


class UpdateCartItem(BaseModel):
    quantity: int = Field(ge=1, le=99)


class CheckoutRequest(BaseModel):
    shipping_address: str = Field(min_length=3, max_length=255)


def cart_payload(db: Session, participant_id: int):
    rows = (
        db.query(CartItem, Product)
        .join(Product, Product.id == CartItem.product_id)
        .filter(CartItem.participant_id == participant_id)
        .order_by(CartItem.id)
        .all()
    )
    items = [
        {
            "product_id": product.id,
            "name": product.name,
            "price": product.price,
            "image": product.image,
            "quantity": item.quantity,
            "line_total": product.price * item.quantity,
        }
        for item, product in rows
    ]
    return {"items": items, "total": sum(item["line_total"] for item in items)}


@router.get("")
def get_cart(
    db: Session = Depends(get_db),
    user: Participant = Depends(get_current_user),
):
    return cart_payload(db, user.id)


@router.post("/items")
def add_cart_item(
    payload: AddCartItem,
    db: Session = Depends(get_db),
    user: Participant = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    item = (
        db.query(CartItem)
        .filter(
            CartItem.participant_id == user.id,
            CartItem.product_id == payload.product_id,
        )
        .first()
    )
    if item:
        item.quantity = min(99, item.quantity + payload.quantity)
    else:
        db.add(
            CartItem(
                participant_id=user.id,
                product_id=payload.product_id,
                quantity=payload.quantity,
            )
        )
    db.commit()
    return cart_payload(db, user.id)


@router.patch("/items/{product_id}")
def update_cart_item(
    product_id: int,
    payload: UpdateCartItem,
    db: Session = Depends(get_db),
    user: Participant = Depends(get_current_user),
):
    item = (
        db.query(CartItem)
        .filter(
            CartItem.participant_id == user.id,
            CartItem.product_id == product_id,
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    item.quantity = payload.quantity
    db.commit()
    return cart_payload(db, user.id)


@router.delete("/items/{product_id}")
def remove_cart_item(
    product_id: int,
    db: Session = Depends(get_db),
    user: Participant = Depends(get_current_user),
):
    deleted = (
        db.query(CartItem)
        .filter(
            CartItem.participant_id == user.id,
            CartItem.product_id == product_id,
        )
        .delete()
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.commit()
    return cart_payload(db, user.id)


@router.post("/checkout", status_code=201)
def checkout(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    user: Participant = Depends(get_current_user),
):
    address = payload.shipping_address.strip()
    if len(address) < 3:
        raise HTTPException(status_code=422, detail="Enter a valid shipping address")

    rows = (
        db.query(CartItem, Product)
        .join(Product, Product.id == CartItem.product_id)
        .filter(CartItem.participant_id == user.id)
        .all()
    )
    if not rows:
        raise HTTPException(status_code=400, detail="Your cart is empty")

    order_id = (db.query(func.max(Order.id)).scalar() or 0) + 1
    total = sum(product.price * item.quantity for item, product in rows)
    order = Order(
        id=order_id,
        participant_id=user.id,
        status="Processing",
        total=total,
        shipping_address=address,
    )
    db.add(order)
    db.flush()
    db.add_all(
        [
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
            )
            for item, product in rows
        ]
    )
    db.query(CartItem).filter(CartItem.participant_id == user.id).delete(
        synchronize_session=False
    )
    db.commit()
    return {"message": "Checkout complete", "order_id": order.id, "total": total}
