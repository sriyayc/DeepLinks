from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Participant
from ..auth import create_session, set_session_cookie, get_current_user

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/login")
def login(token: str, response: Response, db: Session = Depends(get_db)):
    participant = db.query(Participant).filter(Participant.access_token == token).first()
    if not participant:
        raise HTTPException(status_code=401, detail="Invalid login token")

    session_id = create_session(db, participant.id)
    set_session_cookie(response, session_id)

    return {
        "participant_id": participant.id,
        "display_name": participant.display_name,
        "message": "Login successful",
    }


@router.get("/me")
def me(user: Participant = Depends(get_current_user)):
    return {"participant_id": user.id, "display_name": user.display_name}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session_id", path="/")
    return {"message": "Logged out"}