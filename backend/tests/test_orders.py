import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import CartItem, ChatLog, Order, OrderItem, Participant, Product, UserSession
from app.routes import orders


class OrdersApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.Session = sessionmaker(bind=cls.engine, autoflush=False, autocommit=False)
        Base.metadata.create_all(cls.engine)

        test_app = FastAPI()
        test_app.include_router(orders.router)

        def override_db():
            db = cls.Session()
            try:
                yield db
            finally:
                db.close()

        test_app.dependency_overrides[get_db] = override_db
        cls.client = TestClient(test_app)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()

    def setUp(self):
        db = self.Session()
        try:
            for model in (CartItem, ChatLog, OrderItem, Order, UserSession, Product, Participant):
                db.query(model).delete()
            db.add_all(
                [
                    Participant(id=1001, display_name="Alice", access_token="alice-token"),
                    Participant(id=1002, display_name="Bob", access_token="bob-token"),
                    Product(id=1, name="Workshop kit", description="Test product", price=999),
                    Order(
                        id=11,
                        participant_id=1001,
                        status="Delivered",
                        total=999,
                        shipping_address="Alice Street",
                    ),
                    Order(
                        id=27,
                        participant_id=1002,
                        status="Shipped",
                        total=1998,
                        shipping_address="Bob Avenue",
                    ),
                    OrderItem(id=1, order_id=11, product_id=1, quantity=1),
                    OrderItem(id=2, order_id=27, product_id=1, quantity=2),
                    UserSession(session_id="alice-session", participant_id=1001),
                ]
            )
            db.commit()
        finally:
            db.close()

        self.client.cookies.clear()
        self.client.cookies.set("session_id", "alice-session")

    def test_authenticated_participant_only_lists_own_orders(self):
        response = self.client.get("/api/orders")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([order["id"] for order in response.json()], [11])

    def test_unauthenticated_participant_cannot_list_orders(self):
        self.client.cookies.clear()
        self.assertEqual(self.client.get("/api/orders").status_code, 401)

    def test_authenticated_participant_can_open_own_order(self):
        response = self.client.get("/api/orders/11")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["shipping_address"], "Alice Street")

    def test_nonexistent_order_returns_404(self):
        self.assertEqual(self.client.get("/api/orders/9999").status_code, 404)

    def test_intentional_idor_allows_another_participants_order(self):
        response = self.client.get("/api/orders/27")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["participant_id"], 1002)
        self.assertEqual(response.json()["shipping_address"], "Bob Avenue")

    def test_strict_authorization_hides_another_participants_order(self):
        self.assertEqual(self.client.get("/api/orders/27?strict_authz=true").status_code, 404)

    def test_strict_authorization_allows_the_owners_order(self):
        self.assertEqual(self.client.get("/api/orders/11?strict_authz=true").status_code, 200)

    def test_no_token_form_changes_only_current_participants_address(self):
        response = self.client.post(
            "/api/orders/shipping-address",
            data={"shipping_address": "666 Attacker Avenue"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["updated_orders"], 1)

        db = self.Session()
        try:
            self.assertEqual(db.query(Order).filter_by(id=11).one().shipping_address, "666 Attacker Avenue")
            self.assertEqual(db.query(Order).filter_by(id=27).one().shipping_address, "Bob Avenue")
        finally:
            db.close()

    def test_shipping_address_change_requires_a_session(self):
        self.client.cookies.clear()
        response = self.client.post(
            "/api/orders/shipping-address",
            data={"shipping_address": "666 Attacker Avenue"},
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
