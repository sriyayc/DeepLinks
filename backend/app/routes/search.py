from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Product
from ..catalog import serialize_product

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("")
def search(
    q: str = Query(default=""),
    db: Session = Depends(get_db),
):
    # Escape LIKE wildcards: '%' and '_' in a search are literal characters.
    term = q.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    pattern = f"%{term}%"
    products = (
        db.query(Product)
        .filter(Product.name.ilike(pattern, escape="\\"))
        .order_by(Product.id)
        .all()
    )

    return {
        "query": q,
        "results": [serialize_product(product) for product in products],
    }
