import unittest

from types import SimpleNamespace
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.catalog import PRODUCT_CATEGORIES, serialize_product
from app.models import Product
from app.product_seed import seed_products


class CatalogTests(unittest.TestCase):
    def test_every_seeded_product_has_a_category(self):
        from app.product_seed import SAMPLE_PRODUCTS

        self.assertEqual(
            {product["name"] for product in SAMPLE_PRODUCTS},
            set(PRODUCT_CATEGORIES),
        )
        self.assertTrue(all(product["image"] for product in SAMPLE_PRODUCTS))

    def test_iphone_has_numeric_order_price(self):
        from app.product_seed import SAMPLE_PRODUCTS

        iphone = next(product for product in SAMPLE_PRODUCTS if product["name"] == "iPhone Trio")
        self.assertEqual(iphone["price"], 349999)

    def test_seed_repairs_legacy_catalog_without_overwriting_custom_art(self):
        engine = create_engine("sqlite:///:memory:")
        Product.__table__.create(engine)
        with Session(engine) as db:
            db.add_all([
                Product(name="Security Handbook", description="Legacy", price=699, image="/images/book.svg"),
                Product(name="Python Book", description="Legacy", price=499, image=None),
                Product(name="iPhone Trio", description="Legacy", price=0, image="/custom/iphone.png"),
            ])
            db.commit()

            seed_products(db)
            db.commit()

            self.assertEqual(db.query(Product).count(), 14)
            self.assertEqual(db.query(Product).filter_by(name="Security Handbook").one().image, "/images/book.png")
            self.assertEqual(db.query(Product).filter_by(name="Python Book").one().image, "/images/python-book.png")
            iphone = db.query(Product).filter_by(name="iPhone Trio").one()
            self.assertEqual(iphone.image, "/custom/iphone.png")
            self.assertEqual(iphone.price, 349999)
        engine.dispose()

    def test_serialized_product_contains_category(self):
        product = SimpleNamespace(
            id=1,
            name="Python Book",
            description="Learn Python",
            price=499,
            image=None,
        )
        self.assertEqual(serialize_product(product)["category"], "Books")

    def test_unknown_product_uses_other(self):
        product = SimpleNamespace(
            id=99,
            name="Future Product",
            description="Unknown catalog item",
            price=1,
            image=None,
        )
        self.assertEqual(serialize_product(product)["category"], "Other")


if __name__ == "__main__":
    unittest.main()
