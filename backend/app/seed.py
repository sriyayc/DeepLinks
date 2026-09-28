import secrets
import random

from .database import Base, engine, SessionLocal
from .models import Participant, Product, Order, OrderItem
from .product_seed import seed_products

PARTICIPANT_START = 1001
PARTICIPANT_END = 1120  # inclusive -> 120 participants

SAMPLE_ADDRESSES = [
    "10 Example Street",
    "20 Example Avenue",
    "5 Workshop Lane",
    "88 Demo Boulevard",
    "42 Test Court",
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    seed_products(db)
    db.commit()

    products = db.query(Product).all()

    if db.query(Participant).count() == 0:
        participants = [
            Participant(
                id=pid,
                display_name=f"participant{pid}",
                access_token=secrets.token_hex(24),
            )
            for pid in range(PARTICIPANT_START, PARTICIPANT_END + 1)
        ]
        db.add_all(participants)
        db.commit()

    # Mark a few participants as admins for the privilege-escalation lab.
    # IDs 1001, 1002, 1003 are the documented admin accounts.
    ADMIN_IDS = [1001, 1002, 1003]
    db.query(Participant).filter(Participant.id.in_(ADMIN_IDS)).update(
        {Participant.role: "admin"}, synchronize_session="fetch"
    )
    db.commit()

    if db.query(Order).count() == 0:
        participants = db.query(Participant).all()
        order_id = 1
        for p in participants:
            for _ in range(random.randint(2, 5)):
                product = random.choice(products)
                order = Order(
                    id=order_id,
                    participant_id=p.id,
                    status=random.choice(["Processing", "Shipped", "Delivered"]),
                    total=product.price,
                    shipping_address=random.choice(SAMPLE_ADDRESSES),
                )
                db.add(order)
                db.add(OrderItem(order_id=order_id, product_id=product.id, quantity=random.randint(1, 3)))
                order_id += 1
        db.commit()

    db.close()


if __name__ == "__main__":
    seed()
