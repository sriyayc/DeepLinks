from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Participant, UserSession
from ..auth import create_session, set_session_cookie, get_current_user
from ..config import settings

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
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if session_id:
        db.query(UserSession).filter(UserSession.session_id == session_id).delete()
        db.commit()
    response.delete_cookie(
        "session_id",
        path="/",
        httponly=settings.SESSION_COOKIE_HTTPONLY,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        secure=settings.SESSION_COOKIE_SECURE,
    )
    return {"message": "Logged out"}
