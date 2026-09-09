from .database import Base, engine, SessionLocal
from .models import User, Product, Order, OrderItem

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).count() == 0:
        db.add_all([
            User(username="alice", password="alice123"),
            User(username="bob", password="bob123"),
            User(username="charlie", password="charlie123"),
        ])
        db.commit()

    if db.query(Product).count() == 0:
        db.add_all([
            Product(name="Security Handbook", description="A fictional application-security handbook.", price=699, image="/images/book.svg"),
            Product(name="USB Lab Kit", description="A fictional hardware lab kit.", price=999, image="/images/kit.svg"),
            Product(name="Network Adapter", description="A fictional network-testing adapter.", price=1499, image="/images/adapter.svg"),
            Product(name="Cyber Laptop", description="A fictional workshop laptop.", price=75000, image="/images/laptop.svg"),
        ])
        db.commit()

    if db.query(Order).count() == 0:
        db.add_all([
            Order(id=1001, user_id=1, status="Delivered", total=699, shipping_address="10 Example Street"),
            Order(id=1002, user_id=1, status="Processing", total=999, shipping_address="10 Example Street"),
            Order(id=1003, user_id=2, status="Shipped", total=1499, shipping_address="20 Example Avenue"),
            Order(id=1004, user_id=2, status="Delivered", total=699, shipping_address="20 Example Avenue"),
        ])
        db.commit()

        db.add_all([
            OrderItem(order_id=1001, product_id=1, quantity=1),
            OrderItem(order_id=1002, product_id=2, quantity=1),
            OrderItem(order_id=1003, product_id=3, quantity=1),
            OrderItem(order_id=1004, product_id=1, quantity=1),
        ])
        db.commit()

    db.close()

if __name__ == "__main__":
    seed()
