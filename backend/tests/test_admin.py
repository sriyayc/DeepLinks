import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import CartItem, ChatLog, Order, OrderItem, Participant, Product, UserSession
from app.routes import admin


class AdminApiTests(unittest.TestCase):
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
        test_app.include_router(admin.router)

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
                    Participant(id=1001, display_name="Alice", access_token="alice-token", role="admin"),
                    Participant(id=1002, display_name="Bob", access_token="bob-token", role="participant"),
                    UserSession(session_id="alice-session", participant_id=1001),
                    UserSession(session_id="bob-session", participant_id=1002),
                ]
            )
            db.commit()
        finally:
            db.close()

        self.client.cookies.clear()

    # ------------------------------------------------------------------
    # Vulnerable state (strict_authz off — the default)
    # ------------------------------------------------------------------

    def test_non_admin_can_list_users_by_default(self):
        """The intentional vulnerability: any authenticated user sees all users."""
        self.client.cookies.set("session_id", "bob-session")
        response = self.client.get("/api/admin/users")
        self.assertEqual(response.status_code, 200)
        ids = [u["id"] for u in response.json()]
        self.assertIn(1001, ids)
        self.assertIn(1002, ids)

    def test_admin_can_list_users_by_default(self):
        self.client.cookies.set("session_id", "alice-session")
        response = self.client.get("/api/admin/users")
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_request_returns_401(self):
        response = self.client.get("/api/admin/users")
        self.assertEqual(response.status_code, 401)

    # ------------------------------------------------------------------
    # Fixed state (strict_authz on)
    # ------------------------------------------------------------------

    def test_strict_authz_blocks_non_admin(self):
        """With the fix toggle, non-admin participants get 403."""
        self.client.cookies.set("session_id", "bob-session")
        response = self.client.get("/api/admin/users?strict_authz=true")
        self.assertEqual(response.status_code, 403)

    def test_strict_authz_allows_admin(self):
        self.client.cookies.set("session_id", "alice-session")
        response = self.client.get("/api/admin/users?strict_authz=true")
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # Response shape
    # ------------------------------------------------------------------

    def test_response_contains_expected_fields(self):
        self.client.cookies.set("session_id", "alice-session")
        users = self.client.get("/api/admin/users").json()
        for u in users:
            self.assertEqual(set(u), {"id", "display_name", "email", "role"})


if __name__ == "__main__":
    unittest.main()
