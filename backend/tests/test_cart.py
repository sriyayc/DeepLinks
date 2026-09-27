import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import CartItem, Order, OrderItem, Participant, Product
from app.routes.cart import (
    AddCartItem,
    CheckoutRequest,
    UpdateCartItem,
    add_cart_item,
    checkout,
    remove_cart_item,
    update_cart_item,
)


class CartTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = Participant(id=1001, display_name="participant1001", access_token="token")
        self.db.add_all(
            [
                self.user,
                Product(id=1, name="Python Book", description="Book", price=499, image=None),
                Product(id=2, name="Wireless Mouse", description="Mouse", price=799, image=None),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_add_increment_update_and_remove(self):
        result = add_cart_item(AddCartItem(product_id=1, quantity=1), self.db, self.user)
        self.assertEqual(result["total"], 499)

        result = add_cart_item(AddCartItem(product_id=1, quantity=2), self.db, self.user)
        self.assertEqual(result["items"][0]["quantity"], 3)
        self.assertEqual(result["total"], 1497)

        result = update_cart_item(1, UpdateCartItem(quantity=2), self.db, self.user)
        self.assertEqual(result["total"], 998)

        result = remove_cart_item(1, self.db, self.user)
        self.assertEqual(result, {"items": [], "total": 0})

    def test_checkout_creates_order_items_and_clears_cart(self):
        add_cart_item(AddCartItem(product_id=1, quantity=2), self.db, self.user)
        add_cart_item(AddCartItem(product_id=2, quantity=1), self.db, self.user)

        result = checkout(
            CheckoutRequest(shipping_address="10 Workshop Lane"),
            self.db,
            self.user,
        )

        self.assertEqual(result["total"], 1797)
        order = self.db.query(Order).filter_by(id=result["order_id"]).one()
        self.assertEqual(order.participant_id, self.user.id)
        self.assertEqual(order.shipping_address, "10 Workshop Lane")
        self.assertEqual(self.db.query(OrderItem).filter_by(order_id=order.id).count(), 2)
        self.assertEqual(self.db.query(CartItem).count(), 0)


if __name__ == "__main__":
    unittest.main()
