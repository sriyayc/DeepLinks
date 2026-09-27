"""Regression tests for the Task 3 orders/IDOR workshop flow.

Run from ``backend/`` with ``python -m unittest discover -s tests``.
"""

import os
import tempfile
import unittest
from pathlib import Path


# This must be set before importing the application database module.
TEST_DATABASE = Path(tempfile.gettempdir()) / "cybercart-orders-tests.sqlite3"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE}"

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Order, OrderItem, Participant, Product, UserSession


class OrdersApiTests(unittest.TestCase):
    """Exercise orders through the application's existing cookie auth helper."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        if TEST_DATABASE.exists():
            TEST_DATABASE.unlink()

    def setUp(self):
        db = SessionLocal()
        try:
            db.query(OrderItem).delete()
            db.query(Order).delete()
            db.query(UserSession).delete()
            db.query(Product).delete()
            db.query(Participant).delete()

            db.add_all(
                [
                    Participant(id=1001, display_name="Alice", access_token="alice-token"),
                    Participant(id=1002, display_name="Bob", access_token="bob-token"),
                    Product(
                        id=1,
                        name="Workshop kit",
                        description="Test product",
                        price=999,
                    ),
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

        response = self.client.get("/api/orders")

        self.assertEqual(response.status_code, 401)

    def test_authenticated_participant_can_open_own_order(self):
        response = self.client.get("/api/orders/11")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["shipping_address"], "Alice Street")

    def test_nonexistent_order_returns_404(self):
        response = self.client.get("/api/orders/9999")

        self.assertEqual(response.status_code, 404)

    def test_intentional_idor_allows_another_participants_order(self):
        """Expected workshop behavior: default detail access has no ownership check."""
        response = self.client.get("/api/orders/27")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 27)
        self.assertEqual(response.json()["participant_id"], 1002)
        self.assertEqual(response.json()["shipping_address"], "Bob Avenue")

    def test_strict_authorization_hides_another_participants_order(self):
        response = self.client.get("/api/orders/27?strict_authz=true")

        self.assertEqual(response.status_code, 404)

    def test_strict_authorization_allows_the_owners_order(self):
        response = self.client.get("/api/orders/11?strict_authz=true")

        self.assertEqual(response.status_code, 200)
