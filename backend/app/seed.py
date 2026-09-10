import secrets
import random

from .database import Base, engine, SessionLocal
from .models import Participant, Product, Order, OrderItem

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

    if db.query(Product).count() == 0:
        db.add_all([
            Product(name="Security Handbook", description="A fictional application-security handbook.", price=699, image="/images/book.svg"),
            Product(name="USB Lab Kit", description="A fictional hardware lab kit.", price=999, image="/images/kit.svg"),
            Product(name="Network Adapter", description="A fictional network-testing adapter.", price=1499, image="/images/adapter.svg"),
            Product(name="Cyber Laptop", description="A fictional workshop laptop.", price=75000, image="/images/laptop.svg"),
        ])
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