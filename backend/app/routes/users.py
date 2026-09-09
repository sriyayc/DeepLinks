from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User

router = APIRouter(prefix="/api", tags=["users"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.username == body.username, User.password == body.password)
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "user": {
            "id": user.id,
            "username": user.username,
        },
        "message": "Demo login successful",
    }
