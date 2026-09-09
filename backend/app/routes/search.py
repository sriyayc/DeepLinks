from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Product

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("")
def search(
    q: str = Query(default=""),
    db: Session = Depends(get_db),
):
    products = (
        db.query(Product)
        .filter(Product.name.ilike(f"%{q}%"))
        .all()
    )

    return {
        "query": q,
        "results": [
            {"id": p.id, "name": p.name, "price": p.price}
            for p in products
        ],
    }
