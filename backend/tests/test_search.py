import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Product
from app.routes.search import search


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Product.__table__.create(self.engine)
        self.db = Session(self.engine)
        self.db.add_all([
            Product(id=3, name="Pony XM5 Headphones", description="Noise cancelling for study", price=30000, image=None),
            Product(id=1, name="Python Book", description="Practice with beginner exercises", price=499, image=None),
            Product(id=2, name="100%_Kit", description="A kit with a literal percent and underscore", price=999, image="/images/kit.svg"),
        ])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def results(self, query):
        return search(q=query, db=self.db)["results"]

    def test_case_insensitive_name_search(self):
        self.assertEqual([p["id"] for p in self.results("pYtHoN")], [1])
        self.assertEqual([p["id"] for p in self.results("HEADPHONES")], [3])

    def test_description_words_do_not_match(self):
        self.assertEqual(self.results("CANCELLING"), [])
        self.assertEqual(self.results("BEGINNER"), [])

    def test_whitespace_and_empty_search(self):
        self.assertEqual([p["id"] for p in self.results("  python  ")], [1])
        self.assertEqual([p["id"] for p in self.results("")], [1, 2, 3])

    def test_wildcards_are_literal(self):
        self.assertEqual([p["id"] for p in self.results("%")], [2])
        self.assertEqual([p["id"] for p in self.results("_")], [2])
        self.assertEqual(self.results("\\"), [])

    def test_missing_matches_and_sql_like_input(self):
        self.assertEqual(self.results("unicorn"), [])
        self.assertEqual(self.results("' OR 1=1 --"), [])
        self.assertEqual(self.db.query(Product).count(), 3)

    def test_payload_is_returned_as_data_for_frontend_demo(self):
        payload = "<script>alert('XSS demo')</script>"
        response = search(q=payload, db=self.db)
        self.assertEqual(response["query"], payload)
        self.assertEqual(response["results"], [])

    def test_full_card_fields(self):
        product = self.results("100%")[0]
        self.assertEqual(set(product), {"id", "name", "description", "price", "image", "category"})
        self.assertEqual(product["image"], "/images/kit.svg")
        self.assertEqual(product["category"], "Other")


if __name__ == "__main__":
    unittest.main()
