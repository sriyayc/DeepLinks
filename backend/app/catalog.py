"""Presentation metadata for the fixed fictional workshop catalog."""

from .models import Product


PRODUCT_CATEGORIES = {
    "Security Handbook": "Books",
    "Python Book": "Books",
    "Network Fundamentals": "Books",
    "USB Lab Kit": "Electronics",
    "Network Adapter": "Electronics",
    "Cyber Laptop": "Electronics",
    "Wireless Mouse": "Electronics",
    "Headphones": "Electronics",
    "iPhone Trio": "Electronics",
    "Pony XM5 Headphones": "Electronics",
    "Laptop Sleeve": "Accessories",
    "Backpack": "Accessories",
    "Cable Organiser": "Accessories",
    "Desk Mat": "Accessories",
}


def serialize_product(product: Product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "image": product.image,
        "category": PRODUCT_CATEGORIES.get(product.name, "Other"),
    }
