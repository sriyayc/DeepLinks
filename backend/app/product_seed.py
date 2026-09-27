"""Fictional catalog data for task 2; safe to add to an existing workshop DB."""

from sqlalchemy.orm import Session

from .models import Product


LEGACY_IMAGE_PATHS = {
    "/images/book.svg": "/images/book.png",
    "/images/kit.svg": "/images/kit.png",
    "/images/adapter.svg": "/images/adapter.png",
    "/images/laptop.svg": "/images/laptop.png",
}


SAMPLE_PRODUCTS = [
    dict(name="Security Handbook", description="A fictional application-security handbook.", price=699, image="/images/book.png"),
    dict(name="USB Lab Kit", description="A fictional hardware lab kit.", price=999, image="/images/kit.png"),
    dict(name="Network Adapter", description="A fictional network-testing adapter.", price=1499, image="/images/adapter.png"),
    dict(name="Cyber Laptop", description="A fictional workshop laptop.", price=75000, image="/images/laptop.png"),
    dict(name="Python Book", description="A beginner-friendly guide to Python with examples and practice exercises. Fictional workshop product.", price=499, image="/images/python-book.png"),
    dict(name="Network Fundamentals", description="An introduction to computer networks, protocols, and the internet. Fictional workshop product.", price=599, image="/images/network-fundamentals.png"),
    dict(name="Wireless Mouse", description="A compact wireless mouse for everyday study and work. Fictional workshop product.", price=799, image="/images/wireless-mouse.png"),
    dict(name="Headphones", description="Comfortable over-ear headphones for music and online classes. Fictional workshop product.", price=1999, image="/images/headphones.png"),
    dict(name="Laptop Sleeve", description="A padded sleeve to keep a laptop protected on the move. Fictional workshop product.", price=699, image="/images/laptop-sleeve.png"),
    dict(name="Backpack", description="An everyday backpack with a laptop compartment and space for books. Fictional workshop product.", price=1499, image="/images/backpack.png"),
    dict(name="Cable Organiser", description="A compact pouch to keep charging cables and small accessories tidy. Fictional workshop product.", price=299, image="/images/cable-organiser.png"),
    dict(name="Desk Mat", description="A wide desk mat with a smooth surface for a keyboard and mouse. Fictional workshop product.", price=499, image="/images/desk-mat.png"),
    # Orders retain a valid numeric total while the frontend displays the joke label.
    dict(name="iPhone Trio", description="Three fictional iPhones in one very ambitious bundle. Workshop product only.", price=349999, image="/images/iphone-trio.png"),
    dict(name="Pony XM5 Headphones", description="Premium noise-cancelling headphones that help you ignore everything except your budget. Fictional parody workshop product.", price=30000, image="/images/pony-xm5-headphones.png"),
]


def seed_products(db: Session) -> None:
    """Add missing sample listings without overwriting existing products or IDs.

    The caller owns the transaction. Names identify these fixed demo products;
    keeping existing IDs preserves references from participants' order items.
    """
    db.flush()
    existing_products = {product.name: product for product in db.query(Product).all()}
    for listing in SAMPLE_PRODUCTS:
        existing = existing_products.get(listing["name"])
        if existing is None:
            db.add(Product(**listing))
            continue

        # Fill assets added by this task without replacing organizer-supplied art.
        if listing["image"] and not existing.image:
            existing.image = listing["image"]
        elif existing.image in LEGACY_IMAGE_PATHS:
            existing.image = LEGACY_IMAGE_PATHS[existing.image]

        # Repair preview databases created while this joke product used zero.
        if listing["name"] == "iPhone Trio" and existing.price == 0:
            existing.price = listing["price"]
