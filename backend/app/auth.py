from fastapi import Header, HTTPException
from sqlalchemy.orm import Session
from .models import User

# Workshop-only authentication helper.
# Replace with proper sessions/JWTs if you later want production-like auth.
def get_current_user(db: Session, x_user_id: int | None = Header(default=None)):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Login required")

    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid demo user")

    return user
