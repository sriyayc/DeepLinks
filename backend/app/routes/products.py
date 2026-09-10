from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Product
from ..catalog import serialize_product

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("")
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.id).all()
    return [serialize_product(product) for product in products]

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize_product(product)
